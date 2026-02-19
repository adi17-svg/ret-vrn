"""
Low Mood Tool: Gentle Distraction
Permission + Activity Selection + Adaptive + Spiral-Aware
Independent GPT Version
"""

from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT_BASE = """
You suggest small neutral distractions.

Rules:
- Gentle tone
- No pressure
- Keep it simple
- No deep analysis
- Activities must be safe and low-effort
"""

# ---------------------------------------------------
# SPIRAL CLASSIFIER (INTERNAL ONLY)
# ---------------------------------------------------

def classify_spiral(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": """
Classify the user's mindset tendency into one word only:
BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW.

Respond with one word only.
"""
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------
# YES / NO CLASSIFIER
# ---------------------------------------------------

def classify_yes_no(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Classify into one word: YES, NO, or UNCLEAR."},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------
# ACTIVITY TYPE CLASSIFIER
# ---------------------------------------------------

def classify_activity_type(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Classify into one word: MOVEMENT, SENSORY, or MENTAL."
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------
# MOOD SHIFT CLASSIFIER
# ---------------------------------------------------

def classify_shift(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Classify into one word: BETTER, SAME, or WORSE."
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------
# GPT CORE (SPIRAL-AWARE)
# ---------------------------------------------------

def gpt_reply(history: list | None, instruction: str, spiral_stage: str | None) -> str:

    messages = []

    # Base system prompt
    system_prompt = SYSTEM_PROMPT_BASE

    # Inject spiral context (hidden personalization)
    if spiral_stage:
        system_prompt += f"""
        
User tendency appears closer to {spiral_stage}.
Adjust tone subtly to match that mindset,
but never mention stages.
"""

    messages.append({"role": "system", "content": system_prompt})

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------
# MAIN HANDLER
# ---------------------------------------------------

def handle(step: str | None, user_text: str | None, history: list | None = None):

    history = history or []

    # Spiral stage detection (only when user speaks)
    spiral_stage = None
    if user_text:
        spiral_stage = classify_spiral(user_text)

    # =================================================
    # STEP 1 — ASK PERMISSION
    # =================================================
    if step is None or step == "start":

        text = gpt_reply(
            history,
            """
Ask gently:
"Would it feel okay to try a small two-minute distraction together?"

Keep it optional.
""",
            spiral_stage
        )

        return {"step": "permission", "text": text}

    # =================================================
    # STEP 2 — HANDLE PERMISSION
    # =================================================
    if step == "permission":

        decision = classify_yes_no(user_text or "")

        if decision == "YES":
            text = gpt_reply(
                history,
                """
Ask what kind of small activity feels easier right now:
- Light movement
- Sensory (touch, sound, sight)
- Something simple for the mind
""",
                spiral_stage
            )
            return {"step": "choose_type", "text": text}

        if decision == "NO":
            text = gpt_reply(
                history,
                "Acknowledge gently and let them know that's completely okay.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        text = gpt_reply(
            history,
            "Gently ask if they'd like to try something small or just sit together.",
            spiral_stage
        )
        return {"step": "permission", "text": text}

    # =================================================
    # STEP 3 — ACTIVITY TYPE
    # =================================================
    if step == "choose_type":

        activity_type = classify_activity_type(user_text or "")

        if activity_type == "MOVEMENT":
            instruction = "Suggest one very light two-minute movement activity."
        elif activity_type == "SENSORY":
            instruction = "Suggest one gentle two-minute sensory activity."
        else:
            instruction = "Suggest one simple two-minute mental activity."

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "try_activity", "text": text}

    # =================================================
    # STEP 4 — AFTER ACTIVITY
    # =================================================
    if step == "try_activity":

        text = gpt_reply(
            history,
            """
After the activity, ask gently:
"How do you feel now? Even slightly different, or about the same?"
""",
            spiral_stage
        )

        return {"step": "check_mood", "text": text}

    # =================================================
    # STEP 5 — CHECK MOOD
    # =================================================
    if step == "check_mood":

        result = classify_shift(user_text or "")

        if result == "BETTER":
            text = gpt_reply(
                history,
                "Acknowledge the small shift warmly and close gently.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        if result == "SAME":
            text = gpt_reply(
                history,
                "Normalize that it's okay if nothing changed. Ask if they'd like to try one more small activity.",
                spiral_stage
            )
            return {"step": "retry_permission", "text": text}

        if result == "WORSE":
            text = gpt_reply(
                history,
                "Acknowledge gently and suggest stopping. Invite one slow breath instead.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

    # =================================================
    # STEP 6 — RETRY OPTION
    # =================================================
    if step == "retry_permission":

        decision = classify_yes_no(user_text or "")

        if decision == "YES":
            text = gpt_reply(
                history,
                "Suggest a different small two-minute activity.",
                spiral_stage
            )
            return {"step": "try_activity", "text": text}

        text = gpt_reply(
            history,
            "Reassure them they can stop anytime and close gently.",
            spiral_stage
        )
        return {"step": "exit", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {
        "step": "exit",
        "text": "Pausing here is okay."
    }
