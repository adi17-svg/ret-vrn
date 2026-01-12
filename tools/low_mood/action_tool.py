"""
Getting Going With Action Tool
GOAL = START_ACTION
Hybrid: Rule-based logic + OpenAI wording polish
"""

import os
from openai import OpenAI

# OpenAI client (API key .env / Render env var मधून)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _polish_with_llm(text: str) -> str:
    """
    Uses OpenAI ONLY to improve tone & naturalness.
    Does NOT allow structure, goal, or step change.
    """
    prompt = f"""
You are polishing a response for a mental health action tool.

STRICT RULES:
- Do NOT change the meaning
- Do NOT add advice
- Do NOT remove or add steps
- Do NOT change the structure (4 parts)
- Do NOT add extra questions
- Keep it concise (same length or shorter)

Only make the language warmer, softer, and more natural.

Response to polish:
{text}
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,   # creativity but safe
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # fallback → raw text (tool must never break)
        return text


def process_action_tool(entry: str, stage: str | None, mood: str | None):
    """
    Wysa-style fixed flow:
    1. Acknowledge
    2. Redirect to GOAL
    3. Ask permission
    4. Offer small step
    """

    # -------------------------
    # 1️⃣ Acknowledge
    # -------------------------
    if mood in ["sad", "tired", "overwhelmed", "stressed"]:
        acknowledge = "I hear you. When energy is low, starting can feel heavy."
    else:
        acknowledge = "I hear you. Getting started can feel harder than expected."

    # -------------------------
    # 2️⃣ Spiral-based STEP SHAPING (RULED)
    # -------------------------
    if stage == "Red":
        step = "Do it for just 60 seconds. No planning."
    elif stage == "Blue":
        step = "Pick one clear step and follow it."
    elif stage == "Orange":
        step = "What’s the smallest win you can get right now?"
    elif stage == "Green":
        step = "Choose a gentle step that feels kind to you."
    elif stage == "Yellow":
        step = "Notice what part of this is easiest to begin with."
    else:
        step = "Let’s start very small, just one tiny action."

    # -------------------------
    # 3️⃣ Redirect to GOAL
    # -------------------------
    redirect = "Let’s focus only on starting, not finishing."

    # -------------------------
    # 4️⃣ Permission + Step
    # -------------------------
    permission = "Would you be open to trying something very small?"
    offer = f"→ {step}"

    # -------------------------
    # RAW (RULE-BASED) RESPONSE
    # -------------------------
    raw_response = (
        f"{acknowledge}\n\n"
        f"{redirect}\n\n"
        f"{permission}\n"
        f"{offer}"
    )

    # -------------------------
    # LLM POLISH (OPTIONAL, SAFE)
    # -------------------------
    final_response = _polish_with_llm(raw_response)

    return {
        "response": final_response,
        "goal": "START_ACTION"
    }
