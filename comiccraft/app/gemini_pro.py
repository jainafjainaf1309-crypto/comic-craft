import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

MOCK_AI = os.getenv("MOCK_AI", "true").lower() == "true"

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if not MOCK_AI and API_KEY:
    client = genai.Client(api_key=API_KEY)


def generate_story(prompts: list) -> str:

    # MOCK MODE
    if MOCK_AI:
        return """
The Adventure of Arjun

Panel 1:
Arjun enters a mysterious forest and notices a glowing path.

Panel 2:
He follows the path and discovers a small magical creature.

Panel 3:
The creature tells Arjun that the forest is in danger.

Panel 4:
Arjun bravely helps the creature protect the magical forest.

Panel 5:
The forest becomes peaceful again, and Arjun returns home happily.
"""

    # REAL GEMINI MODE
    if not client:
        return "Error: GEMINI_API_KEY not configured."

    prompt_text = " ".join(prompts)

    model_name = "gemini-3.8-flash"

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
            )

            if response.text:
                return response.text

            return "Error generating story: Gemini returned an empty response."

        except Exception as e:
            error_message = str(e)

            if "503" in error_message or "UNAVAILABLE" in error_message:
                if attempt < 2:
                    time.sleep(5)
                    continue

            return f"Error generating story: {error_message}"

    return "Error generating story: Gemini service is temporarily unavailable."