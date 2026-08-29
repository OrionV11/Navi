from ..base_agent import BaseAgent  # Adjust import based on your structure
import json
import os
import requests
import datetime


class GenerateResume(BaseAgent):
    def __init__(self, profile_md_path):
        """Initialize Resume Builder with profile path"""
        super().__init__(
            name="Resume Builder",
            role="Generate Resume",
            goal="Build a tailored Resume"
        )
        
        # Set up file paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, "..", "..", "data", "python_jobs.json")
        self.profile_md_path = profile_md_path
        
        # Load profile
        self.my_profile = self.load_profile()
        
        # Local Ollama API endpoint
        self.local_model_url = "http://127.0.0.1:11434/api/generate"
        
        # Create output directory for resumes
        self.output_dir = os.path.join(script_dir, "..", "..", "data", "resume")
        os.makedirs(self.output_dir, exist_ok=True)
    
    
    def _load_data(self):
        """Load JSON File with job data"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
        
            # Extract jobs from nested structure
            if 'data' in data and 'jobs' in data['data']:
                jobs = data['data']['jobs']
                print(f"Successfully loaded {len(jobs)} jobs from {self.file_path}")
                return jobs
            else:
                print("Error: 'data.jobs' not found in JSON")
                return None
            
        except FileNotFoundError as e:
            print(f"Error loading file: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

    def load_profile(self):
        """Load your personal profile from markdown"""
        try:
            with open(self.profile_md_path, 'r') as f:
                profile = f.read()
                print(f"Successfully loaded profile from {self.profile_md_path}")
                return profile
        except FileNotFoundError as e:
            print(f"Error loading profile: {e}")
            return ""
    
    def extract_job_requirements(self):
        """Extract requirements from job data by parsing job_description"""
        self.job_data = self._load_data()
        if not self.job_data:
            print("No job data available")
            return []
    
        requirements = set()
    
        # Common tech keywords to look for in job descriptions
        tech_keywords = [
            'python', 'javascript', 'java', 'rust', 'golang', 'node.js',
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi',
            'sql', 'postgresql', 'mysql', 'snowflake', 'mongodb',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'git', 'ci/cd', 'rest api', 'graphql', 'microservices',
            'full-stack', 'frontend', 'backend', 'devops',
            'authentication', 'security', 'testing', 'agile',
            'multithreading', 'api development', 'data warehouse'
        ]
    
        for i, job in enumerate(self.job_data):
            print(f"\nDEBUG Job {i}: Processing...")
            print(f"  - Has 'employer_name': {'employer_name' in job}")
            print(f"  - Has 'job_description': {'job_description' in job}")
        
            # Add employer name
            if 'employer_name' in job:
                employer = job['employer_name']
                print(f"  - Employer: {employer}")
                requirements.add(employer)
        
            # Parse job description for keywords and skills
            if 'job_description' in job:
                description = job['job_description']
                print(f"  - Description length: {len(description)}")
            
                description_lower = description.lower()
            
                # Find matching keywords in description
                found_keywords = []
                for keyword in tech_keywords:
                    if keyword in description_lower:
                        found_keywords.append(keyword)
                        requirements.add(keyword)
            
                print(f"  - Found keywords: {found_keywords}")
    
        print(f"\nDEBUG: Total requirements collected: {len(requirements)}")
        print(f"DEBUG: Requirements: {list(requirements)}")
    
        requirements_list = list(requirements)[:20]
        print(f"Extracted {len(requirements_list)} job requirements")
        for req in requirements_list[:5]:
            print(f"  - {req}")
    
        return requirements_list
    

    def generate_tailored_resume(self):
        """Generate resume tailored to job postings using local Ollama"""
        print("Extracting job requirements...")
        job_requirements = self.extract_job_requirements()
        
        if not job_requirements:
            print("No job requirements extracted")
            return None
        
        prompt = f"""You are a professional resume writer. 

Based on this person's profile and these job postings, create a tailored resume that:
1. Highlights skills matching the job requirements
2. Uses keywords from the job postings
3. Emphasizes relevant experience
4. Is professionally formatted in markdown
5. Shows concrete achievements and metrics
6. Tailors language to match job posting terminology

PERSON'S PROFILE:
{self.my_profile}

JOB POSTING REQUIREMENTS:
{json.dumps(self.job_data, indent=2)[:3000]}

TOP REQUIRED SKILLS & KEYWORDS:
{', '.join(job_requirements)}

Generate a professional, ATS-friendly resume that matches these job requirements. Format with clear sections including:
- Professional Summary
- Technical Skills
- Projects/Experience
- Education
- Key Achievements"""
        
        try:
            print("Calling Ollama to generate resume...")
            response = requests.post(
                self.local_model_url,
                json={
                    "model": "orca-mini",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=600  # 2 minute timeout
            )
            
            if response.status_code == 200:
                resume_content = response.json()['response']
                print("Resume generated successfully")
                return resume_content
            else:
                print(f"Error from Ollama: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("Error: Cannot connect to Ollama. Make sure Ollama is running on localhost:11434")
            print("Run: ollama serve")
            return None
        except requests.exceptions.Timeout:
            print("Error: Ollama request timed out. Try again or increase timeout.")
            return None
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None
    
    def save_resume(self, content, output_path=None):
        """Save Resume to file in data/resume folder"""
        if not content:
            print("No content to save")
            return False
        
        # If no output_path provided, create one with timestamp
        if output_path is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f"resume_{timestamp}.md")
        else:
            # If output_path is just a filename, put it in the resume folder
            if not os.path.dirname(output_path):
                output_path = os.path.join(self.output_dir, output_path)
        
        try:
            with open(output_path, 'w') as f:
                f.write(content)
            print(f"✓ Resume saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving resume: {e}")
            return False
    
    def run(self, output_filename=None):
        """Main method to run the entire resume generation pipeline"""
        print("\n" + "="*50)
        print("RESUME GENERATOR")
        print("="*50 + "\n")
        
        # Generate resume
        resume_content = self.generate_tailored_resume()
        
        if resume_content:
            # Save resume
            self.save_resume(resume_content, output_filename)
            print("\n" + "="*50)
            print("Resume generation complete!")
            print("="*50 + "\n")
            return resume_content
        else:
            print("\nFailed to generate resume")
            return None


# Example usage
if __name__ == "__main__":
    # Path to your profile markdown file
    profile_path = "/home/final/Projects/Navi/src/navi_agent/agents/administration/my_profile.md"  # Change this to your actual path
    
    # Create resume builder
    builder = GenerateResume(profile_path)
    
    # Option 1: Auto-save with timestamp
    builder.run()
    
    # Option 2: Save with specific filename
    # builder.run("python_developer_resume.md")
    
    # Option 3: Generate and get content manually
    # resume_content = builder.generate_tailored_resume()
    # if resume_content:
    #     builder.save_resume(resume_content, "my_custom_resume.md")
