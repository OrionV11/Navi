import ollama
import json
from navi_agent.tools.memory import memory


def parse_and_response(user_input: str) -> str:
    context = memory.get_context()

    full_prompt = f"""
    You are Navi. Use the following context to answer personally.
    
    {context}
    
    Current User Input: "{user_input}"

    Instructions:
    1. If the user mentions a preference (e.g., "I like tea"), call the 'save_fact' tool.
    2. Respond naturally.
    3. Return JSON for reminders as before.
    """

    #Call LLM
    response = ollama.chat(model='navi', messages=[{'role': 'user', 'content': full_prompt}])
    ai_reply = response['message']['content']

    # Save Interaction to History
    memory.add_to_history("user", user_input)
    memory.add_to_history("assistant", ai_reply)
