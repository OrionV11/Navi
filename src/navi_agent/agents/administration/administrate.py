from ..base_agent import BaseAgent
from .scheduler import Scheduler
from ...tools.khal_cal import KhalCalendar


class Administrator(BaseAgent):
    """
    Top-level scheduling administration agent.

    Responsibilities:
    1. Ask Scheduler to generate a schedule.
    2. Check the schedule.
    3. Apply feedback/changes.
    4. Approve the schedule.
    5. Save it to schedule.json.
    6. Synchronize it with khal.
    """

    def __init__(self):
        super().__init__(
            name="Administrator",
            role="Personal Assistant Administration Agent",
            goal="Manage, review, update, and synchronize schedules"
        )

        self.scheduler = Scheduler()
        self.khal_calendar = KhalCalendar()

        self.current_schedule = None
        self.feedback = []

    def generate(self):
        """Generate a new schedule using Scheduler."""

        self.current_schedule = (
            self.scheduler.generate_weekly_schedule()
        )

        return self.current_schedule

    def check(self):
        """Check the current schedule for basic problems."""

        if not self.current_schedule:
            return {
                "valid": False,
                "issues": ["Schedule is empty."]
            }

        issues = []

        if not isinstance(self.current_schedule, dict):
            return {
                "valid": False,
                "issues": ["Schedule must be a dictionary."]
            }

        for day, events in self.current_schedule.items():

            if not isinstance(events, list):
                issues.append(
                    f"{day}: events must be a list."
                )
                continue

            for event in events:

                if not isinstance(event, dict):
                    issues.append(
                        f"{day}: invalid event."
                    )
                    continue

                if not event.get("task"):
                    issues.append(
                        f"{day}: event missing task."
                    )

                if not event.get("start"):
                    issues.append(
                        f"{day}: event missing start time."
                    )

                if not event.get("end"):
                    issues.append(
                        f"{day}: event missing end time."
                    )

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

    def feedback(self, feedback):
        """
        Add feedback and apply it to the current schedule.

        Example:

        {
            "action": "change_time",
            "day": "Monday",
            "task": "Work",
            "start": "10:00",
            "end": "15:00"
        }
        """

        if not feedback:
            return self.current_schedule

        if isinstance(feedback, list):
            self.feedback.extend(feedback)
        else:
            self.feedback.append(feedback)

        for item in self.feedback:
            self._apply_feedback(item)

        self.feedback.clear()

        return self.current_schedule

    def _apply_feedback(self, feedback):
        """Apply one feedback instruction."""

        if not isinstance(feedback, dict):
            return

        action = feedback.get("action")
        day = feedback.get("day")

        if not day:
            return

        if not isinstance(self.current_schedule, dict):
            return

        events = self.current_schedule.setdefault(day, [])

        # Add event
        if action == "add":

            event = {
                "task": feedback.get("task"),
                "start": feedback.get("start"),
                "end": feedback.get("end")
            }

            if all(event.values()):
                events.append(event)

        # Remove event
        elif action == "remove":

            task = feedback.get("task")

            self.current_schedule[day] = [
                event
                for event in events
                if event.get("task") != task
            ]

        # Change event time
        elif action == "change_time":

            task = feedback.get("task")

            for event in events:

                if event.get("task") == task:

                    if feedback.get("start"):
                        event["start"] = feedback["start"]

                    if feedback.get("end"):
                        event["end"] = feedback["end"]

    def approve(self):
        """Approve the current schedule if it passes validation."""

        result = self.check()

        if not result["valid"]:
            return result

        return {
            "valid": True,
            "approved": True,
            "schedule": self.current_schedule
        }

    def synchronize(self):
        """Save the schedule and add its events to khal."""

        if not self.current_schedule:
            raise ValueError(
                "Cannot synchronize an empty schedule."
            )

        self.khal_calendar.save_schedule(
            self.current_schedule
        )

        self.khal_calendar.add_events()

        return True

    def administrate(self, feedback=None):
        """
        Complete administration workflow.

        generate
            ↓
        check
            ↓
        feedback
            ↓
        approve
            ↓
        synchronize
        """

        print("Generating schedule...")

        self.generate()

        print("Checking schedule...")

        check = self.check()

        if not check["valid"]:
            return {
                "success": False,
                "stage": "check",
                "issues": check["issues"]
            }

        if feedback:
            print("Applying feedback...")
            self.feedback(feedback)

        print("Approving schedule...")

        approval = self.approve()

        if not approval["approved"]:
            return {
                "success": False,
                "stage": "approval",
                "issues": approval["issues"]
            }

        print("Synchronizing with khal...")

        self.synchronize()

        return {
            "success": True,
            "schedule": self.current_schedule
        }


if __name__ == "__main__":

    administrator = Administrator()

    result = administrator.administrate()

    if result["success"]:
        print("\nSchedule successfully administered.")
        print(result["schedule"])
    else:
        print("\nSchedule administration failed.")
        print(result)
