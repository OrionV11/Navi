import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()
rapid_api_key = os.getenv("RAPID_API_KEY")
rapid_api_host = "jsearch.p.rapidapi.com"

def search_jobs(query, location, api_key):
    url = "https://jsearch.p.rapidapi.com/search-v2"  # Changed to search-v2
    params = {
        'query': query,
        'location': location,
        'page': '1',
        'num_pages': '1'
    }
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': rapid_api_host
    }
    
    response = requests.get(url, params=params, headers=headers)
    return response.json()

results = search_jobs('python developer', 'San Francisco', rapid_api_key)

# Print dict keys
print("Dict Keys:")
print(results.keys())

# Print the full response pretty-formatted
print("\n\nFull Response (pretty-printed):")
print(json.dumps(results, indent=2)[:1500])

print("\n\ncompleted")
