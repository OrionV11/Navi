import sys
import os
import ollama
import json
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from tools import set_reminder, scheduler, speak_text, search_web

load_dotenv()
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')


def parse_intent(text: str) -> dict:
    try:
        response = ollama.chat(model='navi', messages=[{'role': 'user', 'content': text}])
        content = response['message']['content'].strip()
        content = content.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print(f"Parse Error: {e}")
        return {"type": "chat", "message": "I encountered an error parsing your request."}

def main():
    print("Navi Agent Initialized.")
    print("Type 'quit' to exit.")
    
    try:
        while True:
            user_input = input("\nYou: ").strip()
            if not user_input or user_input.lower() in ['quit', 'exit', 'q']:
                break

            data = parse_intent(user_input)
            intent_type = data.get("type")

            if intent_type == "reminder":
                # Only schedule if it's explicitly a reminder
                task = data.get("task", "Unknown Task")
                delay = data.get("delay_seconds", 10)
                confirmation = set_reminder(task, delay)
                print(f"Navi: {confirmation}")
                speak_text(confirmation)
                
            elif intent_type == "chat":
                # Just chat back
                message = data.get("message", "...")
                print(f"Navi: {message}")
                speak_text(message)

            elif intent_type == "search":
                #Search the web
                search = data.get("task", "...")
                print(f"Navi: {search}")
                search_web(search, BRAVE_API_KEY)

                
            else:
                print("Navi: I didn't quite catch that.")

    except KeyboardInterrupt:
        print("\nShutting down...")
        scheduler.shutdown(wait=False)

if __name__ == '__main__':
    main()   