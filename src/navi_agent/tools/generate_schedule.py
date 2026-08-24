import os
import json
import heapq
import random
from datetime import datetime, date, time, timedelta

class ScheduleGenerator:
    def __init__(self, start_hour: int = 10, end_hour: int = 23):
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
        self.file_path_read = os.path.join(script_dir, "..", "data", "activities.json")
        self.file_path_write = os.path.join(script_dir, "..", "data", "schedule.json")
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
            with open(self.file_path_read, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            return {}
    
    def _save_data(self, data):
        """Save data to JSON file"""
        try:
            with open(self.file_path_write, 'w') as f:
                return json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    
    def generate_weekly(self):
        self.data = self._load_data()
        if not self.data:
            return []
        weekdays = {}
        days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for day in days_list:
            self.priority_queue = []
            current_time = self.schedule_start
            remaining_slot = self.timeslot
            daily_schedule = []


        # Flatten and Push to Heap
            for category, items in self.data.items():
                for item in items:
                    name = item.get('name')
                    ran_val = random.random()
                    duration = item.get('duration')
                    priority = item.get('priority', 99) # Default low priority if missing
                    print(f"Pushing: Priority={priority}, Task={name}")
                    heapq.heappush(self.priority_queue, (priority, ran_val, name, duration))

            # Scheduling Loop
            while self.priority_queue:
                priority, ran_val, task, duration = heapq.heappop(self.priority_queue)
                print(f"Popped: priority={priority} ran_val={ran_val} task={task}")

                try:
                    duration_int = int(duration) if duration else 0
                except ValueError:
                    duration_int = 0

                # Skip if doesn't fit (or use 'break' for strict priority stopping)
                if duration_int > remaining_slot:
                    continue

                task_start = current_time
                task_end = task_start + timedelta(hours=duration_int)

                daily_schedule.append({
                    "task": task,
                    "priority": priority,
                    "start": task_start.strftime("%-I:%M %p"),
                    "end": task_end.strftime("%-I:%M %p"),
                    "duration": duration_int
                })

                #print(f"{priority}. {task} | {task_start.strftime('%-I:%M %p')} - {task_end.strftime('%I:%M %p')}")

                current_time = task_end
                remaining_slot -= duration_int

    
            weekdays[day] = daily_schedule

        self._save_data(weekdays)
        return weekdays



