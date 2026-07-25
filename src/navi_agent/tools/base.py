from abc import ABC, abstractmethod

class Searcher(ABC):
    """Base class for all search types"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    @abstractmethod
    def search(self, query: str) -> str:
        """Perform search and return result as string"""
        pass
    
    @abstractmethod
    def validate_query(self, query: str) -> bool:
        """Check if query is valid for this searcher"""
        pass