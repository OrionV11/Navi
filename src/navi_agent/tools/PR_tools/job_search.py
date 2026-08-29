import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("RAPID_API_KEY")


class JobSearcher():
    """Search for job postings"""

    url = "https://jsearch.p.rapidapi.com/search-v2"


    def __init__(self, query, country, location, date_posted, filename):
        self.query = query              
        self.country = country
        self.location = location
        self.date_posted = date_posted
        

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, "..", "..", "data", filename)
    
    def _save_data(self, data):
        """Save data to JSON file"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def search(self):
        headers = { 
            "X-RapidApi-Key": api_key,
            "Content-Type": "application/json",
            "X-RapidApi-Host": "jsearch.p.rapidapi.com"
                   }
        params = { 
            'query': self.query,
            'country': self.country,
            'location': self.location,
            'date_posted': self.date_posted,
                  }
        response = requests.get(self.url, params=params, headers=headers)
        if response.status_code == 200:
            self._save_data(response.json())
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)

searcher1 = JobSearcher('Python Developer', 'US', 'Wichita Falls', 'week', 'python_jobs.json')

searcher2 = JobSearcher('IT Help Desk', 'US', 'Wichita Falls', 'week', 'IT_jobs.json')

searcher3 = JobSearcher('Cybersecurity', 'US', 'Wichita Falls', 'week', 'Cybersecurity.json')

searcher1.search()
searcher2.search()
searcher3.search()
