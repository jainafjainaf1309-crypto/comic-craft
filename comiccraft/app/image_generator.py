import os
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "black-forest-labs/FLUX.1-schnell"
)

client = InferenceClient(
    api_key=HF_API_KEY,
    provider="auto"
)


def sanitize_filename(prompt: str) -> str:
    clean_prompt = re.sub(r"[^a-zA-Z0-9_\- ]", "", prompt)
    return clean_prompt[:30].strip().replace(" ", "_") + ".png"


def generate_image(prompt: str, filename: str = None) -> str:

    if not HF_API_KEY:
        raise ValueError("HF_API_KEY not found in .env")

    if not filename:
        filename = sanitize_filename(prompt)

    folder = "static/panels"
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)

    comic_prompt = f"""
Create a colorful children's comic book panel.

{prompt}

Style:
2D cartoon comic illustration, colorful, expressive characters,
clean outlines, cinematic lighting, fantasy adventure,
high quality, detailed background, storybook illustration.
"""

    image = client.text_to_image(
        comic_prompt,
        model=HF_IMAGE_MODEL,
        width=768,
        height=768,
        num_inference_steps=4
    )

    image.save(path)

    return path