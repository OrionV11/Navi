import requests
import json
from typing import List, Dict, Any
from .base import Searcher

class MangaSearcher(Searcher):
    """Search for manga updates from MangaUpdates API"""
    
    BASE_URL = 'https://api.mangaupdates.com/v1/releases/days'
    
    def __init__(self):
        super().__init__()
        self.manga_updates = {}
    
    def validate_query(self, query: str) -> bool:
        """Validate if query is asking for manga info"""
        keywords = ['manga', 'chapter', 'update', 'release', 'latest']
        return any(keyword in query.lower() for keyword in keywords)
    
    def search(self, query: str) -> str:
        """Main search method - fetch and return manga data"""
        if not self.validate_query(query):
            return "I'm not sure what manga info you're looking for."
        
        try:
            self.manga_updates = self._fetch_manga_updates()
            return self._format_results(query)
        
        except requests.exceptions.RequestException as e:
            return f"HTTP Error occurred: {e}"
        except json.JSONDecodeError as e:
            return f"JSON parsing error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def _fetch_manga_updates(self) -> Dict[str, str]:
        """Fetch latest manga releases from API"""
        try:
            params = {
                'include_metadata': 'true',
                'page': 1
            }
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()  # Raise error for bad status codes
            
            data = response.json()
            manga_list = {}
            
            print(f"Found {len(data.get('results', []))} manga releases\n")
            
            for release in data.get('results', []):
                try:
                    title = release['metadata']['series']['title']
                    chapter = release['record']['chapter']
                    manga_list[title] = chapter
                except KeyError as e:
                    print(f"Warning: Missing key in release data: {e}")
                    continue
            
            return manga_list
        
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {}
    
    def _format_results(self, query: str) -> str:
        """Format manga updates for display"""
        if not self.manga_updates:
            return "No manga updates found."
        
        result = "Latest Manga Updates:\n"
        
        # Show top 10 updates
        for i, (title, chapter) in enumerate(list(self.manga_updates.items())[:10], 1):
            result += f"\n{i}. {title}\n"
            result += f"   Chapter: {chapter}\n"
        
        return result
    
    def get_raw_data(self) -> Dict[str, str]:
        """Return raw manga data for JSON export"""
        return self.manga_updates
    
    def export_to_json(self, filename: str = 'manga_data.json') -> None:
        """Export manga data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.manga_updates, f, indent=4, ensure_ascii=False)
            print(f"Data exported to {filename}")
        except IOError as e:
            print(f"Error writing file: {e}")
    
    def load_from_json(self, filename: str = 'manga_data.json') -> Dict[str, str]:
        """Load manga data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.manga_updates = json.load(f)
            return self.manga_updates
        except IOError as e:
            print(f"Error reading file: {e}")
            return {}
   

