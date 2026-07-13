from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from plyer import notification
from datetime import datetime, timedelta
from dateutil import tz
from icalendar import Calendar
from msal import PublicClientApplication, SerializableTokenCache
from datetime import timezone
import logging
import psutil
import requests
import os
import pyttsx3
import time
from dotenv import load_dotenv
from memory import memory


load_dotenv()
MORGEN_API_KEY = os.getenv('MORGEN_API_KEY')
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
TIMEZONE = os.getenv('TIMEZONE', 'UTC')

# Configure logging to suppress noisy APScheduler logs
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.ERROR)

engine = pyttsx3.init()



# 1. Define a persistent job store (saves to 'jobs.sqlite' file)
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

# 2. Initialize scheduler with the persistent store
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

def send_notification(task: str):
    """Triggers the native OS notification."""
    notification.notify(
        title='Navi',
        message=f"Hey Listen!: {task}",
        app_name='Navi Agent',
        timeout=10,
        app_icon=''
    )
    print(f"HEY LISTEN: {task}")


def set_reminder(task: str, delay_seconds: int):
    """Schedules a reminder. Survives restarts if delay is long."""
    run_time = datetime.now() + timedelta(seconds=delay_seconds)
    
    # Add job to the 'default' (persistent) store
    scheduler.add_job(
        func=send_notification,
        trigger='date',
        run_date=run_time,
        args=[task],
        id=f"reminder_{datetime.now().timestamp()}",
        jobstore='default',  # Critical: Saves to SQLite
        replace_existing=True
    )
    return f"Reminder set for {task} at {run_time.strftime('%Y-%m-%d %H:%M:%S')}"

def save_fact(fact: str) -> str:
    """Saves a long-term fact about the user."""
    memory.add_fact(fact)
    return f"Fact saved: '{fact}'"


def get_events_for_date(target_date=None):
    """
    Fetches events for a specific date from Google Calendar

    target_date: datetime.date object for the target day

    """

    CALENDAR_URLS = [
        'callurl',
        'call2url'
    ]

    LOCAL_TZ = os.getenv('TIMEZONE', 'Central Time')

    local = tz.gettz(LOCAL_TZ)

    if target_date is None:
        target_date = datetime.now(local).date()

    #Create datetime for the target day boundaries
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = day_start - timedelta(days=1)

    # Debug: Print the date range we're checking
    print(f"\n[Debug] Checking calendars for date: {target_date.strftime('%Y-%m-%d')}")
    print(f"  Start: {day_start.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"  End: {day_end.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"  Timezone: {LOCAL_TZ}")
    
    all_events = []
    
    # Fetch from each calendar
    for idx, cal_url in enumerate(CALENDAR_URLS, 1):
        calendar_name = f"Calendar {idx}"
        print(f"\n[Debug] Fetching {calendar_name}...")
        
        try:
            # Load calendar from ICS URL with adequate timeout
            r = requests.get(cal_url, timeout=30)
            r.raise_for_status()
            cal = Calendar(r.text)
            
            events_found_this_cal = 0
            total_events_in_cal = len(list(cal.events))
            print(f"  Total events in {calendar_name}: {total_events_in_cal}")
            
            # Use timeline to efficiently filter events for target day's date range
            # Convert local times to UTC for timeline filtering
            day_start_utc = day_start.astimezone(timezone.utc)
            day_end_utc = day_end.astimezone(timezone.utc)
            
            # Get events in target day's range using timeline
            days_timeline = cal.timeline.overlapping(day_start_utc, day_end_utc)
            
            for e in days_timeline:
                if not e.begin:
                    continue
                    
                # Get event start time
                start = e.begin.datetime
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                
                # Convert to local timezone
                start_local = start.astimezone(local)
                
                # Debug: Print first few events to see dates
                if events_found_this_cal < 3:
                    print(f"  Event: '{e.name}' at {start_local.strftime('%Y-%m-%d %H:%M')}")
                
                # Get end time
                end = e.end.datetime if e.end else None
                end_local = end.astimezone(local) if end else None
                
                all_events.append({
                    "title": e.name,
                    "start": start_local.strftime("%H:%M"),
                    "end": end_local.strftime("%H:%M") if end_local else None,
                    "location": e.location or "",
                    "description": e.description or ""
                })
                events_found_this_cal += 1
            
            print(f"  [OK] Found {events_found_this_cal} event(s) for target day in {calendar_name}")
            
        except requests.exceptions.RequestException as e:
            print(f"  [X] Network error fetching {calendar_name}: {str(e)}")
            continue
        except Exception as e:
            print(f"  [X] Error processing {calendar_name}: {type(e).__name__}: {str(e)}")
            continue
    
    # Sort by start time
    all_events.sort(key=lambda x: x["start"])
    
    # Print all events in detail
    if all_events:
        print(f"\n[Google Calendar] Found {len(all_events)} event(s) for {target_date.strftime('%Y-%m-%d')}:")
        print("-" * 60)
        for event in all_events:
            time_str = f"{event['start']}-{event['end']}" if event['end'] else event['start']
            location_str = f" @ {event['location']}" if event['location'] else ""
            print(f"  {time_str} | {event['title']}{location_str}")
        print("-" * 60)
    else:
        print(f"\n[Google Calendar] No events for {target_date.strftime('%Y-%m-%d')}")
    
    return all_events


def get_tasks(target_date=None):
    """
    Fetches tasks from Morgen for a specific date
    """
    MORGEN_API_KEY = os.getenv('MORGEN_API_KEY')
    if not MORGEN_API_KEY:
        print("[Morgen To Do] Missing MORGEN_API_KEY environment variable")
        return []
    
    # Set target date
    if target_date is None:
        from datetime import date
        target_date = date.today()
    
    # Prepare headers - note: "ApiKey" not "Bearer"
    headers = {
        "accept": "application/json",
        "Authorization": f"ApiKey {MORGEN_API_KEY}"
    }
    
    try:
        # Fetch tasks from Morgen API
        params = {
            "limit": 100
        }
        
        response = requests.get(
            "https://api.morgen.so/v3/tasks/list",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        tasks_list = data.get("data", {}).get("tasks", [])
        all_tasks = []
        
        # Parse tasks
        for task in tasks_list:
            # Skip completed tasks
            if task.get("progress") == "completed":
                continue
            
            due_str = task.get("due")
            if not due_str:
                continue
            
            try:
                # Parse LocalDateTime format (e.g., "2023-03-15T17:00:00")
                due_date = datetime.fromisoformat(due_str)
                
                # Get timezone from task, fallback to UTC
                tz_name = task.get("timeZone", "UTC")
                try:
                    local_tz = tz.gettz(tz_name)
                    if local_tz:
                        due_date = due_date.replace(tzinfo=local_tz)
                    else:
                        due_date = due_date.replace(tzinfo=timezone.utc)
                except:
                    due_date = due_date.replace(tzinfo=timezone.utc)
                
                target_day_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                target_day_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
                
                # Convert due_date to UTC for comparison
                if due_date.tzinfo:
                    due_date_utc = due_date.astimezone(timezone.utc)
                else:
                    due_date_utc = due_date.replace(tzinfo=timezone.utc)
                
                # Determine status
                if due_date_utc < target_day_start:
                    status = "OVERDUE"
                elif due_date_utc <= target_day_end:
                    status = f"DUE {target_date.strftime('%Y-%m-%d')}"
                else:
                    status = "FUTURE"
                
                # Map priority: 1 = highest, 9 = lowest, 0 = undefined
                priority_map = {
                    0: "undefined",
                    1: "highest",
                    2: "very-high",
                    3: "high",
                    4: "medium-high",
                    5: "medium",
                    6: "medium-low",
                    7: "low",
                    8: "very-low",
                    9: "lowest"
                }
                priority = priority_map.get(task.get("priority", 0), "normal")
                
                all_tasks.append({
                    "id": task.get("id"),
                    "list": task.get("taskListId", "default"),
                    "title": task.get("title"),
                    "description": task.get("description", ""),
                    "due": due_date.strftime("%Y-%m-%d %H:%M"),
                    "duration": task.get("estimatedDuration", ""),
                    "priority": priority,
                    "status": task.get("progress", "needs-action"),
                    "due_status": status,
                    "tags": task.get("tags", [])
                })
            except Exception as e:
                print(f"[Morgen] Error parsing task '{task.get('title', 'Unknown')}': {e}")
                continue
        
        # Sort by due date
        all_tasks.sort(key=lambda x: x["due"])
        
        # Print summary
        if all_tasks:
            print(f"[Morgen To Do] {len(all_tasks)} task(s) for {target_date.strftime('%Y-%m-%d')} or overdue")
            for task in all_tasks:
                if task["due_status"] != "FUTURE":
                    print(f"  {task['due']} | {task['title']} [{task['priority']}]")
        else:
            print(f"[Morgen To Do] No tasks due on {target_date.strftime('%Y-%m-%d')}")
        
        return all_tasks
        
    except requests.exceptions.RequestException as e:
        print(f"[Morgen To Do] Network error: {e}")
        return []
    except Exception as e:
        print(f"[Morgen To Do] Error: {type(e).__name__}: {e}")
        return []
    


def get_system_status():
    #CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    #Memory Usage
    memory = psutil.virtual_memory()

    #Disk Usage
    disk = psutil.disk_usage('/')

    format = (
        f"""Memory Used: {memory.percent}%
            \nDisk Used: {disk.percent}%
            \nCPU Used: {cpu_percent}%

        """)
    
    return format



def subscriptsion():
    pass