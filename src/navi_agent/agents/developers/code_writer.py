from ..base_agent import BaseAgent

class CodeWriter(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Code Writer",
            role="Expert code generator",
            goal="Write clean, well-documented code"
        )
    
    def run(self, task: str) -> str:
        system_prompt = """You are a Code Writer Agent.
Your job is to generate clean, working Python code.

Always:
1. Write readable code with comments
2. Follow PEP 8 standards
3. Use meaningful variable names
4. Include error handling
5. Add docstrings

Provide ONLY the code, nothing else."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        return self.call_model(messages)

if __name__ == "__main__":
    agent = CodeWriter()
    result = agent.run("Create a function that checks if a number is prime")
    print(result)
