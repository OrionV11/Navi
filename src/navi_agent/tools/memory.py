import os
import ollama
import json
from datetime import datetime

DATA_DIR = "data"
MEMORY_FILE = os.path.join(DATA_DIR,  "memory.json")


class AgentMemory:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        return {
            "user_prefs": {"name": "User", "timezone": "UTC"},
            "facts": [],
            "conversation_history": []
        }
    
    def save(self):
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_fact(self, fact: str):
        """Adds a long-term fact (persists forever)."""
        self.data["facts"].append({"content": fact, "created": datetime.now().isoformat()})
        self.save()

    def add_to_history(self, role: str, content: str):
        """Adds to short-term conversation history"""
        self.data["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context(self) -> str:
        """Builds a context string for the LLM."""
        prefs = self.data["user_prefs"]
        facts = "\n".join([f"- {f['content']}" for f in self.data["facts"][-5:]]) # Last 5 facts
        history = "\n".join([f"{m['role']}: {m['content']}" for m in self.data['conversation_history']])

        return f"""
        [User Preferences]
        Name: {prefs.get('name', 'User')}

        [Known Facts]
        {facts if facts else "None yet."}

        [Recent Conversation]
        {history if history else "No recent conversation."}
        """

memory = AgentMemory