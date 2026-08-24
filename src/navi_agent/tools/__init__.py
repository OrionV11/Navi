"""Tools package for Navi agent."""

from typing import Optional
from .web_search import WebSearcher
from .reminders import ReminderManager
from .personal_assistant import PersonalAssistantManager


def get_searcher(api_key: Optional[str] = None) -> WebSearcher:
    """
    Factory function to get a WebSearcher instance.
    
    Args:
        api_key: Brave Search API key
        
    Returns:
        WebSearcher instance
    """
    if not api_key:
        raise ValueError("Brave API key is required for WebSearcher")
    return WebSearcher(api_key)


def get_reminder_manager() -> ReminderManager:
    """
    Factory function to get a ReminderManager instance.
    
    Returns:
        ReminderManager instance
    """
    return ReminderManager()


def get_personal_assistant(name: str = "Navi") -> PersonalAssistant:
    """
    Factory function to get a PersonalAssistant instance.
    
    Args:
        name: Name for the assistant
        
    Returns:
        PersonalAssistant instance
    """
    return PersonalAssistantManager(name)


__all__ = [
    'get_searcher',
    'get_reminder_manager',
    'get_personal_assistant'
]
