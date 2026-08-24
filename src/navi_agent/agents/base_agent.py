import requests

class BaseAgent:
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.model = "Navi"
        self.base_url = "http://localhost:11434"
    
    def call_model(self, messages: list) -> str:
        """Call Ollama locally"""
        response = requests.post(
            f'{self.base_url}/api/chat',
            json={'model': self.model, 'messages': messages, 'stream': False}
        )
        return response.json()['message']['content']
    
    def run(self, task: str) -> str:
        """Run agent - override in subclasses"""
        system_prompt = f"You are {self.name}. Role: {self.role}. Goal: {self.goal}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        return self.call_model(messages)
