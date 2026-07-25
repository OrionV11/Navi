import os
import json
import heapq
from datetime import datetime, date, time, timedelta

class ScheduleGenerator:
    def __init__(self, start_hour: int = 10, end_hour: int = 22):
        """
        Initialize the generator.
        Only accept configuration parameters here, not the data itself.
        """
        today = date.today()

        # Configuration
        self.start_hour = start_hour
        self.end_hour = end_hour
        
        # File Path Setup
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, "..", "data", "activities.json")
        
        # Time Calculation
        self.start_day = datetime.combine(date.today(), time.min)
        self.schedule_start = datetime.combine(today, time(start_hour,0,0))
        days_offset = 1 if end_hour < start_hour else 0
        self.schedule_end = datetime.combine(today, time(end_hour,0,0)) + timedelta(days=days_offset)
        self.timeslot = int((self.schedule_end - self.schedule_start).total_seconds() / 3600)

        self.priority_queue = []
        self.data = {} # Initialize empty

    def _load_data(self) -> dict:
        """Import data from the JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            return {}

    def generate(self) -> list:
        """Generates the schedule based on the loaded JSON data."""
        self.data = self._load_data()
        if not self.data:
            return []

        schedule = []

        current_time = self.schedule_start
        remaining_slot = self.timeslot

        # Flatten and Push to Heap
        for category, items in self.data.items():
            for item in items:
                name = item.get('name')
                duration = item.get('duration')
                priority = item.get('priority', 99) # Default low priority if missing
                heapq.heappush(self.priority_queue, (priority, name, duration))

        # Scheduling Loop
        while self.priority_queue:
            priority, task, duration = heapq.heappop(self.priority_queue)

            try:
                duration_int = int(duration) if duration else 0
            except ValueError:
                duration_int = 0

            # Skip if doesn't fit (or use 'break' for strict priority stopping)
            if duration_int > remaining_slot:
                continue

            task_start = current_time
            task_end = task_start + timedelta(hours=duration_int)

            schedule.append({
                "task": task,
                "priority": priority,
                "start": task_start.strftime("%-I:%M %p"),
                "end": task_end.strftime("%-I:%M %p"),
                "duration": duration_int
            })

            #print(f"{priority}. {task} | {task_start.strftime('%-I:%M %p')} - {task_end.strftime('%I:%M %p')}")

            current_time = task_end
            remaining_slot -= duration_int
    
        return schedule

    def generate_weekly(self, schedule_data):

        weekdays = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[]}
        for week, items in weekdays.items():
                items.append(schedule_data)
        print(weekdays)
        return weekdays


# --- How to Call It ---
# No arguments needed if defaults (10 AM - 10 PM) are fine
generator = ScheduleGenerator() 
final_schedule = generator.generate()

weekly_schedule = generator.generate_weekly(final_schedule)