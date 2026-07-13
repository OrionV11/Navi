import requests
from typing import List, Dict, Any
from .base import Searcher
import ollama

class WebSearcher(Searcher):
    """Web search using Brave Search API with snippet summarization"""
    
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if not api_key:
            raise ValueError("Brave API key is required for WebSearcher")
    
    def validate_query(self, query: str) -> bool:
        """Validate search query"""
        return len(query.strip()) > 0
    
    def search(self, query: str) -> str:
        """Perform web search and return ONE best answer"""
        if not self.validate_query(query):
            return "Please provide a valid search query."
        
        try:
            results = self._fetch_results(query)
            best_result = self._find_best_result(results)
            return self._format_result(best_result, query)
        
        except requests.exceptions.RequestException as e:
            return f"Search failed: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def _fetch_results(self, query: str) -> List[Dict[str, Any]]:
        """Fetch top 3 results from Brave API"""
        brave_headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": 3
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, headers=brave_headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if 'web' in data and 'results' in data['web']:
                return data['web']['results']
            else:
                return []
        except Exception as e:
            print(f"Error fetching from Brave: {e}")
            return []
    
    def _clean_snippet(self, snippet: str) -> str:
        """Remove HTML tags and clean up snippet"""
        # Remove HTML tags
        snippet = snippet.replace('<strong>', '').replace('</strong>', '')
        snippet = snippet.replace('&quot;', '"').replace('&#39;', "'")
        snippet = snippet.replace('&amp;', '&')
        
        # Remove excessive whitespace
        snippet = ' '.join(snippet.split())
        
        return snippet
    
    def _summarize_snippet(self, snippet: str, title: str, query: str) -> str:
        """Use Ollama to clean and summarize the snippet into a clear answer"""
        try:
            prompt = f"""Answer the question: "{query}"

Using this information:
Title: {title}
Content: {snippet}

Provide a direct, clear 1-2 sentence answer. Be factual and specific. Do not add opinions or meta-commentary."""
            
            response = ollama.chat(
                model='navi',
                messages=[
                    {'role': 'system', 'content': 'You are a factual information provider. Give direct, clear answers based on the information provided.'},
                    {'role': 'user', 'content': prompt}
                ],
                stream=False
            )
            
            answer = response['message']['content'].strip()
            
            # Validate we got a real answer
            if answer and len(answer) > 10 and not answer.startswith('{'):
                return answer
            else:
                # Fallback to cleaned snippet if Ollama fails
                return self._clean_snippet(snippet)[:200]
        
        except Exception as e:
            print(f"Error summarizing: {e}")
            # Fallback to cleaned snippet
            return self._clean_snippet(snippet)[:200]
    
    def _find_best_result(self, results: List[Dict]) -> Dict:
        """Find the result with the best snippet"""
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]
        
        # Pick the result with the longest snippet (usually most informative)
        best = max(results, key=lambda r: len(r.get('description', '')))
        return best
    
    def _format_result(self, result: Dict, query: str) -> str:
        """Format single result for display"""
        if not result:
            return f"No results found for '{query}'"
        
        title = result.get('title', 'Unknown')
        snippet = result.get('description', 'No description available')
        url = result.get('url', '')
        
        # Clean and summarize the snippet
        cleaned_snippet = self._clean_snippet(snippet)
        summary = self._summarize_snippet(cleaned_snippet, title, query)
        
        output = f"Answer to '{query}':\n\n"
        output += f"{title}\n"
        output += f"{summary}\n"
        output += f"Source: {url}"
        
        return output