import os
import fitz  # PyMuPDF
import docx
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import BaseTool

# --- 1. Local LLM Configuration (Ollama) ---
# Ensure Ollama is running: ollama serve
local_llm = LLM(
    model="ollama/llama3.1",  # Or 'qwen2.5-coder' for better logic
    base_url="http://localhost:11434",
    temperature=0.3  # Lower temp for factual resume writing
)

# --- 2. Custom Tool: Resume Parser ---
class ResumeParserTool(BaseTool):
    name: str = "Resume Parser"
    description: str = "Extracts text from a PDF or DOCX resume file path."

    def _run(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return "Error: File not found."
        
        text = ""
        if file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            return "Error: Unsupported format. Use PDF or DOCX."
        return text

# --- 3. Define Agents ---
strategist_agent = Agent(
    role="Senior Resume Strategist",
    goal="Critique the resume and identify missing keywords based on the job description.",
    backstory="You are an expert recruiter who knows exactly what ATS systems look for. You provide harsh but constructive feedback.",
    llm=local_llm,
    tools=[ResumeParserTool()],
    verbose=True,
    allow_delegation=False
)

writer_agent = Agent(
    role="Professional Resume Writer",
    goal="Rewrite the resume sections to incorporate missing keywords and improve impact without lying.",
    backstory="You are a professional writer who specializes in tailoring resumes to specific job descriptions. You write in clear, action-oriented Markdown.",
    llm=local_llm,
    verbose=True,
    allow_delegation=False
)

# --- 4. Define Tasks ---
# Task 1: Analyze
analyze_task = Task(
    description=(
        "1. Use the Resume Parser tool to read the file at: {file_path}\n"
        "2. Compare the resume content against this Job Description: {job_description}\n"
        "3. Identify 5-10 missing keywords or skills.\n"
        "4. Provide a score (1-10) and specific bullet points on what to change."
    ),
    expected_output="A critique report with a score and a list of missing keywords/improvements.",
    agent=strategist_agent
)

# Task 2: Rewrite
rewrite_task = Task(
    description=(
        "1. Take the original resume text and the critique from the previous task.\n"
        "2. Rewrite the 'Professional Summary' and 'Work Experience' sections to naturally include the missing keywords.\n"
        "3. Ensure the tone is professional and action-oriented.\n"
        "4. Output the FULL new resume in Markdown format."
    ),
    expected_output="A complete, tailored resume in Markdown format.",
    agent=writer_agent,
    context=[analyze_task]  # Passes the output of analyze_task to this task
)

# --- 5. Assemble Crew ---
def run_resume_crew(file_path: str, job_description: str):
    crew = Crew(
        agents=[strategist_agent, writer_agent],
        tasks=[analyze_task, rewrite_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff(inputs={
        "file_path": file_path,
        "job_description": job_description
    })
    return result

if __name__ == "__main__":
    # Test run
    pass   