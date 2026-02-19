"""
Low Mood Tool: Breath Word
Permission + Multi-Cycle + Adaptive + Spiral-Aware
Independent GPT Version
"""

from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT_BASE = """
You are a calm breathing guide.

Rules:
- Keep responses short (1–3 lines)
- Gentle tone
- Clear guidance
- No analysis
- No advice
- Keep instructions simple
"""

# ---------------------------------------------------
# SPIRAL CLASSIFIER (INTERNAL)
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
            {
                "role": "system",
                "content": "Classify the response into one word only: YES, NO, or UNCLEAR."
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

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust tone subtly to match that mindset,
but never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------
# MAIN HANDLER
# ---------------------------------------------------

def handle(step: str | None, user_text: str | None, history: list | None = None):

    history = history or []

    # Detect Spiral stage only if user speaks
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
"Would it feel okay to try a short breathing moment together?"

Keep it optional and soft.
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
Guide the first slow inhale with the word "here"
and exhale with "now".

Keep it calm and steady.
""",
                spiral_stage
            )
            return {"step": "cycle_2", "text": text}

        if decision == "NO":
            text = gpt_reply(
                history,
                """
Acknowledge gently.
Let them know that's completely okay.
Offer to stay present in another way.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        text = gpt_reply(
            history,
            """
Gently ask if they'd prefer to breathe together,
or just talk instead.
""",
            spiral_stage
        )
        return {"step": "permission", "text": text}

    # =================================================
    # BREATH CYCLE 2
    # =================================================
    if step == "cycle_2":
        text = gpt_reply(
            history,
            """
Guide another inhale "here"
and exhale "now".
Stay with the rhythm.
""",
            spiral_stage
        )
        return {"step": "cycle_3", "text": text}

    # =================================================
    # BREATH CYCLE 3
    # =================================================
    if step == "cycle_3":
        text = gpt_reply(
            history,
            """
Guide one final inhale "here"
and exhale "now".

Then gently ask:
"How does your body feel now?"
""",
            spiral_stage
        )
        return {"step": "check_state", "text": text}

    # =================================================
    # CHECK STATE
    # =================================================
    if step == "check_state":
        text = gpt_reply(
            history,
            f"""
The user said: "{user_text}"

Acknowledge gently.
If calmer, affirm.
If not, normalize.
Close softly.
""",
            spiral_stage
        )
        return {"step": "exit", "text": text}

    return {
        "step": "exit",
        "text": "We can pause here."
    }
