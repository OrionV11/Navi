from abc import ABC, abstractmethod
from typing import Optional
import requests
import json


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


class WebSearcher(Searcher):
    """Search the web using DuckDuckGo API (free, no authentication needed)"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.base_url = "https://api.duckduckgo.com"
    
    def validate_query(self, query: str) -> bool:
        """Check if query is valid"""
        return bool(query.strip()) and len(query.strip()) > 0
    
    def search(self, query: str) -> str:
        """Perform search and return result as string"""
        if not self.validate_query(query):
            raise ValueError("Query cannot be empty")
        
        try:
            # DuckDuckGo API endpoint
            params = {
                "q": query,
                "format": "json",
                "no_redirect": 1,
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            output = f"Search results for '{query}':\n\n"
            
            # Add instant answer if available
            if data.get("AbstractText"):
                output += f"Summary:\n{data['AbstractText']}\n\n"
            
            # Add related topics/results
            if data.get("RelatedTopics"):
                topics = data["RelatedTopics"][:5]  # Get first 5 results
                
                for i, topic in enumerate(topics, 1):
                    if isinstance(topic, dict):
                        text = topic.get("Text", "N/A")
                        url = topic.get("FirstURL", "N/A")
                        
                        output += f"{i}. {text}\n"
                        output += f"   Link: {url}\n\n"
            
            if not data.get("RelatedTopics") and not data.get("AbstractText"):
                return f"No results found for '{query}'"
            
            return output
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Search failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse search results: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")


def get_searcher(searcher_type: str = "web", api_key: Optional[str] = None) -> Searcher:
    """
    Factory function to get a Searcher instance.
    
    Args:
        searcher_type: Type of searcher to create ('web')
        api_key: Not required for web searcher
        
    Returns:
        Searcher instance
        
    Raises:
        ValueError: If searcher_type is not recognized
    """
    if searcher_type == "web":
        return WebSearcher(api_key=api_key)
    else:
        raise ValueError(
            f"Unknown searcher type: {searcher_type}. "
            f"Available: 'web'"
        )


# Example usage
if __name__ == "__main__":
    searcher = get_searcher("web")
    
    try:
        results = searcher.search("python programming")
        print(results)
    except Exception as e:
        print(f"Error: {e}")
