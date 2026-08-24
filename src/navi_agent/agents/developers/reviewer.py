from ..base_agent import BaseAgent

class Reviewer(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Code Reviewer",
            role="Code quality expert",
            goal="Review and improve code quality"
        )
    
    def run(self, task: str) -> str:
        system_prompt = """You are a Code Reviewer Agent.
Your job is to review and improve code.

Always:
1. Identify strengths
2. Point out issues/improvements
3. Suggest refactoring
4. Check for edge cases
5. Rate quality (1-10)

Provide constructive, actionable feedback."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        return self.call_model(messages)

if __name__ == "__main__":
    agent = Reviewer()
    result = agent.run("Review: x = [1,2,3]; print(sum(x))")
    print(result)
