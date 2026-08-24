import sys
from navi_agent.agents.base_agent import BaseAgent
from navi_agent.tools.generate_schedule import ScheduleGenerator

class Scheduler(BaseAgent):
    def __init__(self):
        super().__init__(
                name="Scheduler",
                role="Personal Assistant Scheduler",
                goal="Schedule calendar, appointments, and reminders"
            )
        self.schedule_generator = ScheduleGenerator()
        
    def generate_weekly_schedule(self):
        return self.schedule_generator.generate_weekly()


