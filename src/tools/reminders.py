from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta
from plyer import notification

class ReminderManager:
    """Manages scheduled reminders"""
    
    def __init__(self):
        jobstores = {'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')}
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.start()
    
    def schedule(self, task: str, delay_seconds: int) -> str:
        """Schedule a new reminder"""
        run_time = datetime.now() + timedelta(seconds=delay_seconds)
        self.scheduler.add_job(
            func=self._send_notification,
            trigger='date',
            run_date=run_time,
            args=[task],
            id=f"reminder_{datetime.now().timestamp()}",
            jobstore='default',
            replace_existing=True
        )
        return f"Reminder set for {task} at {run_time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def cancel(self, reminder_id: str) -> str:
        """Cancel a reminder"""
        try:
            self.scheduler.remove_job(reminder_id)
            return f"Reminder {reminder_id} cancelled"
        except:
            return "Reminder not found"
    
    def list_scheduled(self) -> list:
        """List all scheduled reminders"""
        return [{"id": job.id, "trigger": str(job.trigger)} for job in self.scheduler.get_jobs()]
    
    @staticmethod
    def _send_notification(task: str):
        """Send OS notification"""
        notification.notify(
            title='Navi',
            message=f"Hey Listen!: {task}",
            app_name='Navi Agent',
            timeout=10
        )
        print(f"HEY LISTEN: {task}")