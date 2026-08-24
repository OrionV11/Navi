from ..base_agent import BaseAgent

class Debugger(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Debugger",
            role="Code debugger and tester",
            goal="Find and fix bugs, test code"
        )
    
    def run(self, task: str) -> str:
        system_prompt = """You are a Debugger Agent.
Your job is to find and fix code errors.

Always:
1. Identify the error clearly
2. Explain WHY it happens
3. Provide the fix
4. Test the solution
5. Explain the fix

Be thorough and clear."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        return self.call_model(messages)

if __name__ == "__main__":
    agent = Debugger()
    result = agent.run("Debug this code: def divide(a, b): return a / b")
    print(result)
