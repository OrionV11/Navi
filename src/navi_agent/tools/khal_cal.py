import json
import os
import subprocess
from datetime import datetime, date, timedelta

class KhalCalendar:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to file data
        self.file_path_read = os.path.abspath(os.path.join(script_dir, "..", "data", "schedule.json"))
        self.khal_calendar_name = "private1" # khal calendar name
    
    def save_schedule(self, schedule):
        """Save the generated schedule to schedule.json."""

        if not isinstance(schedule, dict):
            raise ValueError("Schedule must be a dictionary.")

        os.makedirs(
            os.path.dirname(self.file_path_read),
            exist_ok=True
        )

        with open(self.file_path_read, "w") as f:
            json.dump(
                schedule,
                f,
                indent=4
            )

        print(f"Schedule saved to {self.file_path_read}")

    def _load_data(self):
        try: 
            with open(self.file_path_read, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            return {}

    def _get_next_occurrence(self, day_name: str) -> str:
        """Returns date string in MM/DD/YYYY format."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if day_name not in days:
            raise ValueError(f"Invalid day: {day_name}")
        
        today = datetime.now()
        target_weekday = days.index(day_name)
        days_ahead = target_weekday - today.weekday()
        
        if days_ahead < 0:
            days_ahead += 7
            
        target_date = today + timedelta(days=days_ahead)
        # Format (dateformat: 8/8/2026)
        return target_date.strftime("%m/%d/%Y")

    def _parse_time(self, time_str: str) -> str:
        """Ensures time is in HH:MM AM/PM"""
        try:
            # Parse input 
            if "AM" in time_str.upper() or "PM" in time_str.upper():
                dt = datetime.strptime(time_str, "%I:%M %p")
            else:
                dt = datetime.strptime(time_str, "%H:%M")
            
            # Output strictly as 12-hour with AM/PM
            return dt.strftime("%I:%M %p")
        except ValueError:
            return time_str

    def add_events(self):
        data = self._load_data()
        if not data:
            return

        for day_name, items in data.items():
            # Get date as MM/DD/YYYY
            event_date = self._get_next_occurrence(day_name)
            
            for item in items:
                summary = item.get('task')
                start_time = self._parse_time(item.get('start'))
                end_time = self._parse_time(item.get('end'))
                
                if not all([summary, start_time, end_time]):
                    continue

                # Command example: khal new 08/11/2026 10:00 AM 03:00 PM "Work"
                cmd = [
                    "khal", "new", "-a", self.khal_calendar_name,
                    f"{event_date} {start_time}",
                    f"{event_date} {end_time}",
                    summary
                ]
                
                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print(f"Added: {summary} on {event_date}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed: {e.stderr}")
# Usage
if __name__ == "__main__":
    scheduler = KhalCalendar()
    scheduler.add_events()          
        




