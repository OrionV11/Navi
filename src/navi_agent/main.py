import sys
import os
import ollama
import json
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from text_speech import speak_text
from tools.toolkit import scheduler
from tools import get_searcher, get_reminder_manager, get_personal_assistant
from intent_parser import parse_intent
load_dotenv()
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

reminder_manager = get_reminder_manager()
personal_assistant = get_personal_assistant()


def parse_intent(text: str) -> dict:
    system_prompt = """You are an intent classifier. Analyze the user's message and return ONLY valid JSON (no markdown, no backticks).

Classify into one of these types:
1. "reminder" - if user wants to set a reminder/alarm
   Return: {"type": "reminder", "task": "...", "delay_seconds": X}
   
2. "search" - if user wants to search for information
   IMPORTANT: For manga/anime queries, specify the search_type:
   - "manga updates" or "manga chapters" → {"type": "search", "task": "...", "search_type": "manga"}
   - "anime episodes" or "anime updates" → {"type": "search", "task": "...", "search_type": "anime"}
   - Everything else → {"type": "search", "task": "...", "search_type": "web"}
   
3. "chat" - if user just wants to chat or ask a question
   Return: {"type": "chat", "message": "..."}

Examples:
- "new manga updates" → {"type": "search", "task": "new manga updates", "search_type": "manga"}
- "search for AI news" → {"type": "search", "task": "AI news", "search_type": "web"}
- "anime episodes" → {"type": "search", "task": "anime episodes", "search_type": "anime"}
- "find anime updates for One Piece" → {"type": "search", "task": "One Piece anime updates"}
- "remind me to watch in 2 hours" → {"type": "reminder", "task": "watch", "delay_seconds": 7200}
- "how are you?" → {"type": "chat", "message": "I'm doing well!"}

Return ONLY the JSON object, nothing else."""

    try:
        response = ollama.chat(
            model='navi', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text}
            ]
        )
        content = response['message']['content'].strip()
        content = content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Model returned: {content}")  # Debug: see what the model actually returned
        return {"type": "chat", "message": "I encountered an error parsing your request."}
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
                confirmation = reminder_manager.schedule(task, delay)
                print(f"Navi: {confirmation}")
                speak_text(confirmation)
            
            elif intent_type == "calendar":
                events = personal_assistant.get_events()
                
            elif intent_type == "chat":
                # Just chat back
                message = data.get("message", "...")
                print(f"Navi: {message}")
                speak_text(message)

            elif intent_type == "search":
                search_query = data.get("task", "...")
                search_type = data.get("search_type", "web")  # Should be "anime"
    
                searcher = get_searcher(search_type)
                if searcher:
                    result = searcher.search(search_query)
                    print(f"Navi: {result}")
                    speak_text(result)

                
            else:
                print("Navi: I didn't quite catch that.")

    except KeyboardInterrupt:
        print("\nShutting down...")
        scheduler.shutdown(wait=False)

if __name__ == '__main__':
    main()   