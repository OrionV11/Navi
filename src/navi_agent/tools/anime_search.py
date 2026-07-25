import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import feedparser
from typing import List, Dict, Any
from .base import Searcher


class AnimeSearcher(Searcher):
    """Search for anime epidodes and headlines from LiveChart"""
    #RSS feed URLs
    EPISODES_URL = 'https://www.livechart.me/feeds/episodes'
    HEADLINES_URL = 'https://www.livechart.me/feeds/headlines'
    
    def __init__(self):
        super().__init__()
        self.episodes = []
        self.headlines = []
    
    def validate_query(self, query: str) -> bool:
        """Validate if query is asking for anime info"""
        keywords = ['epidsode', 'episodes', 'anime', 'headline', 'update', 'latest']
        return any(keyword in query.lower() for keyword in keywords)

    def search(self, query: str) -> str:
        """Main search method - fetch and return anime data"""
        if not self.validate_query(query):
            return "I'm not sure what anime info you're looking for"
        
        try:
            self.episodes = self._fetch_feed(self.EPISODES_URL, "episodes")
            self.headlines = self._fetch_feed(self.HEADLINES_URL, "headlines")

            #Format and return results
            return self.__format__results(query)
        
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error has occured: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


    def _fetch_feed(self, url: str, feed_type: str) -> list[Dict[str, Any]]:

        try:
            feed = feedparser.parse(url)
            entries = []
            print(f"Found {len(feed.entries)} {feed_type}\n")
            
            for entry in feed.entries:
                entry_data = self._extract_entry(entry)
                entries.append(entry_data)
            
            return entries
        
        except Exception as e:
            print(f"Error fetching {feed_type}: {e}")
            return []


    def _extract_entry(self, entry) -> Dict[str, Any]:
        """
        Extract common data from feed entry
        Handles media_content, enclosures, and image attributes
        """
        title = entry.get('title', 'Unknown')
        link = entry.get('link', '')
        image = None
        
        # Try multiple ways to get image
        if hasattr(entry, 'media_content') and entry.media_content:
            image = entry.media_content[0]['url']
        elif hasattr(entry, 'enclosures') and entry.enclosures:
            image = entry.enclosures[0]['href']
        elif hasattr(entry, 'image') and entry.image:
            image = entry.image
        
        return {
            "Title": title,
            "Link": link,
            "Image": image
        }
        
    def _format_results(self, query: str) -> str:
        """Format results based on query type"""
        query_lower = query.lower()
        
        if 'headline' in query_lower:
            return self._format_headlines()
        elif 'episode' in query_lower:
            return self._format_episodes()
        else:
            # Return both if user didn't specify
            return self._format_both()
    
    def _format_episodes(self) -> str:
        """Format episodes for display"""
        if not self.episodes:
            return "No recent episodes found."
        
        result = "Recent Anime Episodes:\n"
        for ep in self.episodes[:5]:  # Show top 5
            result += f"\n {ep['Title']}\n"
            if ep['Link']:
                result += f"   Link: {ep['Link']}\n"
        return result
    
    def _format_headlines(self) -> str:
        """Format headlines for display"""
        if not self.headlines:
            return "No headlines found."
        
        result = "Anime Headlines:\n"
        for headline in self.headlines[:5]:  # Show top 5
            result += f"\n {headline['Title']}\n"
            if headline['Link']:
                result += f"   Link: {headline['Link']}\n"
        return result
    
    def _format_both(self) -> str:
        """Format both episodes and headlines"""
        result = self._format_episodes()
        result += "\n" + self._format_headlines()
        return result
    
    def get_raw_data(self) -> Dict[str, List]:
        """Return raw data for JSON export"""
        return {
            "episodes": self.episodes,
            "headlines": self.headlines
        }


