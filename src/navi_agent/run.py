from langchain_runner import Runner
from agent import agent

runner = Runner(agent=agent)

@runner.cron("0 9 * * *")  # Runs every day at 9 AM
def daily_task():
    return "Good morning! Here's your daily summary."

runner.serve()