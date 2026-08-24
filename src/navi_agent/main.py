import sys
import os
import ollama
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

from navi_agent.text_speech import speak_text
from navi_agent.tools.toolkit import scheduler
from navi_agent.tools import get_searcher, get_reminder_manager, get_personal_assistant
from navi_agent.agents.developers.agent_team import AgentTeam
from navi_agent.agents.administration.administrate import Administrator


load_dotenv()


# ---------------------------------------------------------
# Initialize agents
# ---------------------------------------------------------

agent_team = AgentTeam()

reminder_manager = get_reminder_manager()

personal_assistant = get_personal_assistant()

brave_api_key = os.getenv("BRAVE_API_KEY")

# Schedule administration agent
administrator = Administrator()


# ---------------------------------------------------------
# Intent parser
# ---------------------------------------------------------

def parse_intent(text: str) -> dict:
    """Parse user intent."""

    system_prompt = """
You are an intent classifier for a personal AI assistant.

Return ONLY valid JSON.

Classify the user's request into one of:

1. "code_workflow" - full code generation workflow
2. "code_with_tests" - generate code with unit tests
3. "fix_code" - fix broken code
4. "refactor" - refactor existing code
5. "optimize" - optimize code
6. "review" - review code only
7. "reminder" - set reminder
8. "search" - search information
9. "chat" - normal conversation
10. "schedule" - generate, modify, review, or synchronize a schedule

For schedule requests, return feedback when appropriate.

Schedule feedback examples:

User:
"Move my Monday work to 10am"

Return:
{
    "type": "schedule",
    "task": "change Monday Work to 10am",
    "feedback": {
        "action": "change_time",
        "day": "Monday",
        "task": "Work",
        "start": "10:00"
    }
}

User:
"Add gym on Tuesday from 6pm to 7pm"

Return:
{
    "type": "schedule",
    "task": "add gym Tuesday",
    "feedback": {
        "action": "add",
        "day": "Tuesday",
        "task": "Gym",
        "start": "18:00",
        "end": "19:00"
    }
}

User:
"Remove gym from Tuesday"

Return:
{
    "type": "schedule",
    "task": "remove gym Tuesday",
    "feedback": {
        "action": "remove",
        "day": "Tuesday",
        "task": "Gym"
    }
}

For a normal schedule generation request:

{
    "type": "schedule",
    "task": "generate my weekly schedule"
}

For other intents return:

{
    "type": "...",
    "task": "..."
}

For code requests include "code" when needed.
"""


    try:
        response = ollama.chat(
            model="navi",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        content = response["message"]["content"].strip()

        # Remove markdown JSON fences if Ollama returns them
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(content)

    except Exception as e:
        print(f"Intent parsing error: {e}")
        return {
            "type": "chat",
            "task": text
        }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("Navi Agent Team Initialized")

    print("\nTry these commands:")
    print("  'generate code to ...' - Full workflow")
    print("  'create with tests ...' - Code + unit tests")
    print("  'fix this code: ...' - Fix broken code")
    print("  'refactor this: ...' - Refactor code")
    print("  'optimize ...' - Optimize code")
    print("  'review ...' - Review code")
    print("  'generate my schedule' - Generate weekly schedule")
    print("  'move Monday work to 10am' - Modify schedule")
    print("  'add gym Tuesday 6pm to 7pm' - Add calendar event")
    print("  'remove gym Tuesday' - Remove calendar event")

    try:

        while True:

            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                break

            # -------------------------------------------------
            # Parse intent
            # -------------------------------------------------

            data = parse_intent(user_input)

            intent_type = data.get("type")

            # -------------------------------------------------
            # CODE WORKFLOW
            # -------------------------------------------------

            if intent_type == "code_workflow":

                task = data.get("task", user_input)

                agent_team.generate_and_review_code(task)

                speak_text("Code generation complete")

            # -------------------------------------------------
            # CODE + TESTS
            # -------------------------------------------------

            elif intent_type == "code_with_tests":

                task = data.get("task", user_input)

                agent_team.create_with_tests(task)

                speak_text("Code and tests generated")

            # -------------------------------------------------
            # FIX CODE
            # -------------------------------------------------

            elif intent_type == "fix_code":

                code = data.get("code", "")

                error = data.get("task", "")

                agent_team.fix_broken_code(
                    code,
                    error
                )

                speak_text("Code fix complete")

            # -------------------------------------------------
            # REFACTOR
            # -------------------------------------------------

            elif intent_type == "refactor":

                code = data.get("code", "")

                goal = data.get(
                    "task",
                    "improve readability"
                )

                agent_team.refactor_code(
                    code,
                    goal
                )

                speak_text("Refactoring complete")

            # -------------------------------------------------
            # OPTIMIZE
            # -------------------------------------------------

            elif intent_type == "optimize":

                code = data.get("code", "")

                agent_team.optimize_code(code)

                speak_text("Optimization complete")

            # -------------------------------------------------
            # REVIEW
            # -------------------------------------------------

            elif intent_type == "review":

                code = data.get("code", "")

                result = agent_team.review_existing_code(
                    code
                )

                print(f"Navi: {result}")

                speak_text("Code review complete")

            # -------------------------------------------------
            # REMINDER
            # -------------------------------------------------

            elif intent_type == "reminder":

                task = data.get(
                    "task",
                    "task"
                )

                confirmation = reminder_manager.schedule(
                    task,
                    10
                )

                print(f"Navi: {confirmation}")

                speak_text(confirmation)

            # -------------------------------------------------
            # SEARCH
            # -------------------------------------------------

            elif intent_type == "search":

                search_query = data.get(
                    "task",
                    ""
                )

                searcher = get_searcher(
                    brave_api_key
                )

                if searcher:

                    result = searcher.search(
                        search_query
                    )

                    print(f"Navi: {result}")

                    speak_text(result)

            # -------------------------------------------------
            # SCHEDULE
            # -------------------------------------------------

            elif intent_type == "schedule":

                task = data.get(
                    "task",
                    user_input
                )

                feedback = data.get(
                    "feedback"
                )

                print("\nNavi: Administrating schedule...")

                try:

                    result = administrator.administrate(
                        feedback=feedback
                    )

                    if result.get("success"):

                        print(
                            "\nNavi: Schedule successfully "
                            "updated and synchronized with khal."
                        )

                        print(
                            json.dumps(
                                result.get("schedule"),
                                indent=4
                            )
                        )

                        speak_text(
                            "Schedule updated and synchronized "
                            "with your calendar"
                        )

                    else:

                        print(
                            "\nNavi: Schedule administration failed."
                        )

                        print(
                            json.dumps(
                                result,
                                indent=4
                            )
                        )

                        speak_text(
                            "I couldn't update the schedule"
                        )

                except Exception as e:

                    print(
                        f"\nNavi: Schedule error: {e}"
                    )

                    speak_text(
                        "There was an error updating the schedule"
                    )

            # -------------------------------------------------
            # CHAT / UNKNOWN
            # -------------------------------------------------

            else:

                print(
                    "Navi: I didn't understand that. "
                    "Try 'generate my schedule' or "
                    "'generate code to ...'"
                )

    except KeyboardInterrupt:

        print("\nShutting down...")

        scheduler.shutdown(
            wait=False
        )


if __name__ == "__main__":
    main()
