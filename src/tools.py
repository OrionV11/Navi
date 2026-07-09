from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger
from plyer import notification
from datetime import datetime, timedelta

scheduler = BlockingScheduler()



#reminder function 
def set_reminder(task: str, delay_seconds: int):
    """ 
    Schedules a reminder using APScheduler
    """

    run_time = datetime.now() + timedelta(seconds=delay_seconds)

    #Add a job
    scheduler.add_job(
        func=send_notification,
        trigger='date',
        run_date=run_time,
        args=[task],
        id=f"reminder_{datetime.now().timestamp()}",
        replace_existing=True
    )

    return f"Reminder set for {task} at {run_time.strftime('%H:%M:%S')}"

def send_notification(task: str):
    """
    Triggers the native OS notification using plyer
    """
    
    notification.notify(
        title='Navi',
        message=f"Hey Listen!: {task}",
        app_name='Navi Agent',
        timeout=10,
        app_icon=''
    )

    print(f" HEY LISTEN: {task}")

import threading
threading.Thread(target=scheduler.start, daemon=True).start()