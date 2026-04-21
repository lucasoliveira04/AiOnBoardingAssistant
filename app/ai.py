from groq import Groq
from typing import List
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_prompt():
    with open("prompt.md", "r", encoding="utf-8") as file:
        return file.read()

SYSTEM_PROMPT = load_prompt()


def generate_onboarding_steps(markdown: str) -> List[dict]:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Documento do projeto:\n\n{markdown}"},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content.strip()
    steps = json.loads(raw)

    return steps