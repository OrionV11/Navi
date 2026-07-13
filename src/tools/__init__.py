from .anime_search import AnimeSearcher
from .manga_search import MangaSearcher
from .web_search import WebSearcher
from .reminders import ReminderManager
from .personal_assistant import PersonalAssistantManager
import os
from dotenv import load_dotenv
load_dotenv()

BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

# Initialize searchers
anime_searcher = AnimeSearcher()
manga_searcher = MangaSearcher()
web_searcher = WebSearcher(api_key=BRAVE_API_KEY)


reminder_manager = ReminderManager()
MORGEN_KEY = os.getenv('MORGEN_API_KEY')
personal_assistant = PersonalAssistantManager(morgen_key=MORGEN_KEY)



SEARCHERS = {
    "anime": anime_searcher,
    "manga": manga_searcher,
    "web": web_searcher
}

def get_searcher(search_type: str):
    """Get the right searcher"""
    return SEARCHERS.get(search_type.lower())

def get_reminder_manager():
    return reminder_manager

def get_personal_assistant():
    return personal_assistant