from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from plyer import notification
from datetime import datetime, timedelta
import logging
from memory import memory

# Configure logging to suppress noisy APScheduler logs
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.ERROR)

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

def speak_text(text: str):
    # Placeholder for TTS
    pass   