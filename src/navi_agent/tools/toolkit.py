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
from tools.memory import memory


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


def save_fact(fact: str) -> str:
    """Saves a long-term fact about the user."""
    memory.add_fact(fact)
    return f"Fact saved: '{fact}'"


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