import requests
import json

class JobSearcher():
    """Search for job postings from Himalayas.app (Remote Jobs API)"""
    
    # Official Himalayas API Endpoint (No auth required)
    HIMALAYAS_API_URL = 'https://himalayas.app/jobs/api/search'
    
    def __init__(self):
        super().__init__()
        self.jobs = []
    
    def validate_query(self, query: str) -> bool:
        """Validate if query is asking for job info"""
        keywords = ['job', 'career', 'position', 'opening', 'employment', 'role', 'hire']
        return any(keyword in query.lower() for keyword in keywords)
    
    def search(self, query: str, location: str = "Worldwide") -> str:
        """Main search method - fetch and return job data from Himalayas API"""
        if not self.validate_query(query):
            return "I'm not sure what job info you're looking for."
        
        try:
            # Himalayas API parameters
            params = {
                'q': query,          # Search keyword (e.g., "Python Developer")
                'page': 1,           # Page number
                'limit': 5           # Number of results (Max 20 per page)
            }
            
            # Note: Himalayas focuses on REMOTE jobs. 
            # Location filtering is done via 'country' or 'timezone' params if needed.
            # If you need specific country filtering, add: 'country': 'US'
            
            self.jobs = self._fetch_himalayas_api(params)
            return self._format_results(query)
        
        except requests.exceptions.RequestException as e:
            return f"HTTP Error occurred: {e}"
        except json.JSONDecodeError as e:
            return f"JSON parsing error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def _fetch_himalayas_api(self, params: dict) -> list[dict]:
        """Fetch jobs from Himalayas official JSON API"""
        try:
            response = requests.get(self.HIMALAYAS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs_list = []
            # The API returns a 'jobs' array inside the response
            raw_jobs = data.get('jobs', [])
            
            print(f"Found {len(raw_jobs)} jobs on Himalayas\n")
            
            for job in raw_jobs:
                job_data = {
                    'title': job.get('title', 'No Title'),
                    'company': job.get('companyName', 'Unknown Company'),
                    'link': job.get('applicationLink', job.get('url', '')),
                    'location': job.get('locationRestriction', ['Remote'])[0] if job.get('locationRestriction') else 'Remote',
                    'salary': f"{job.get('minSalary', '')} - {job.get('maxSalary', '')} {job.get('currency', '')}" if job.get('minSalary') else 'Not listed',
                    'tags': job.get('categories', [])
                }
                jobs_list.append(job_data)
            
            return jobs_list
        
        except Exception as e:
            print(f"Error fetching Himalayas API: {e}")
            return []

    def _format_results(self, query: str) -> str:
        """Format the job list into a readable string for the Agent"""
        if not self.jobs:
            return f"No jobs found for '{query}' on Himalayas."
        
        output = f"Here are the top {len(self.jobs)} remote jobs for '{query}':\n\n"
        for i, job in enumerate(self.jobs, 1):
            output += f"{i}. **{job['title']}** at {job['company']}\n"
            output += f"    {job['location']} |  {job['salary']}\n"
            output += f"    {job['link']}\n\n"
        
        return output

# Example Usage
if __name__ == "__main__":
    job_searcher = JobSearcher()
    # Search for "Python" jobs
    results = job_searcher.search("IT Help Desk")
    print(results)   