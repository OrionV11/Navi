import os
import sys
import ollama
import json

# Add src to path if not already there
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools import set_reminder
from datetime import datetime

def parse_intent(text: str) -> dict:
    """Sends text to Navi model and expects strict JSON."""
    try:
        response = ollama.chat(model='navi', messages=[{'role': 'user', 'content': text}])
        content = response['message']['content'].strip()
        # Clean markdown if present
        content = content.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print(f"Parse Error: {e}")
        return {"task": "Error parsing request", "delay_seconds": 0}

def main():
    print("Navi Agent Initialized.")
    print("Try: 'Remind me to stretch in 10 seconds'")
    
    try:
        while True:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Navi: Farewell, Nushi.")
                break

            # 1. Parse Intent
            data = parse_intent(user_input)
            
            # 2. Execute Tool
            if 'task' in data and 'delay_seconds' in data:
                confirmation = set_reminder(data['task'], data['delay_seconds'])
                print(f"Navi: {confirmation}")
            else:
                print(" Navi: I couldn't understand the time or task.")

    except KeyboardInterrupt:
        print(" Interrupted by user.")

if __name__ == '__main__':
    main()   

