import json
import ollama

def parse_intent(text: str) -> dict:
    """
    Uses Ollama to classify user input into intent types
    Returns a dictionary with the classification and relevant data
    """
    system_prompt = """You are an intent classifier. Analyze the user's message and return ONLY valid JSON (no markdown, no backticks).

Classify into one of these types:

1. "reminder" - if user wants to set a reminder/alarm
   Return: {"type": "reminder", "task": "...", "delay_seconds": X}
   
2. "search" - if user wants to search for information
   IMPORTANT: For manga/anime queries, specify the search_type:
   - "manga updates", "manga chapters", "new manga" → {"type": "search", "task": "...", "search_type": "manga"}
   - "anime episodes", "anime updates", "new anime" → {"type": "search", "task": "...", "search_type": "anime"}
   - Everything else → {"type": "search", "task": "...", "search_type": "web"}
   
3. "calendar" - if user asks about events/calendar
   Return: {"type": "calendar", "action": "get_events", "date": "optional"}
   
4. "tasks" - if user asks about tasks/to-do
   Return: {"type": "tasks", "action": "get_tasks", "date": "optional"}
   
5. "chat" - if user just wants to chat or ask a question
   Return: {"type": "chat", "message": "..."}

Examples:
- "remind me to watch anime in 1 hour" → {"type": "reminder", "task": "watch anime", "delay_seconds": 3600}
- "search for new manga updates" → {"type": "search", "task": "new manga updates", "search_type": "manga"}
- "find anime episodes" → {"type": "search", "task": "anime episodes", "search_type": "anime"}
- "search for AI news" → {"type": "search", "task": "AI news", "search_type": "web"}
- "what's on my calendar" → {"type": "calendar", "action": "get_events"}
- "show my tasks" → {"type": "tasks", "action": "get_tasks"}
- "how are you?" → {"type": "chat", "message": "I'm doing well!"}

Return ONLY the JSON object, nothing else."""

    try:
        response = ollama.chat(
            model='navi',  # Make sure you have this model in Ollama
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text}
            ]
        )
        
        content = response['message']['content'].strip()
        # Remove markdown formatting if present
        content = content.replace('```json', '').replace('```', '').strip()
        
        # Parse and return JSON
        return json.loads(content)
    
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Model returned: {content}")
        return {"type": "chat", "message": "I encountered an error parsing your request."}
    
    except Exception as e:
        print(f"Parse Error: {e}")
        return {"type": "chat", "message": "I encountered an error parsing your request."}