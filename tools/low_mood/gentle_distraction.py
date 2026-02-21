"""
Low Mood Tool: Gentle Distraction (Spiral + Context Aware)

Design:
- Independent GPT usage
- Spiral-aware tone (internal only)
- Uses full chat history
- Clean structured flow
- No cross-tool mixing
- Safe retry logic
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You suggest small neutral distractions.

Rules:
- Gentle tone
- No pressure
- Keep it simple
- No deep analysis
- Activities must be safe and low-effort
- Keep responses short (2–4 lines)
"""

# =====================================================
# SAFE CLASSIFIER
# =====================================================

def safe_classify(system_instruction, user_text, valid_options, default):

    if not user_text or len(user_text.strip()) < 2:
        return default

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip().upper()

        if result in valid_options:
            return result

        return default

    except:
        return default


def classify_spiral(user_text):
    return safe_classify(
        "Classify into one word: BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW.",
        user_text,
        ["BEIGE", "PURPLE", "RED", "BLUE", "ORANGE", "GREEN", "YELLOW"],
        "GREEN"
    )


def classify_activity_type(user_text):
    return safe_classify(
        "Classify into one word: MOVEMENT, SENSORY, or MENTAL.",
        user_text,
        ["MOVEMENT", "SENSORY", "MENTAL"],
        "MENTAL"
    )


def classify_shift(user_text):
    return safe_classify(
        "Classify into one word: BETTER, SAME, or WORSE.",
        user_text,
        ["BETTER", "SAME", "WORSE"],
        "SAME"
    )


def classify_yes_no(user_text):
    return safe_classify(
        "Classify into one word: YES or NO.",
        user_text,
        ["YES", "NO"],
        "NO"
    )


# =====================================================
# GPT REPLY (Context + Spiral Aware)
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust tone subtly.
Never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []
    spiral_stage = classify_spiral(user_text) if user_text else "GREEN"

    # -------------------------------------------------
    # STEP 0 — START (Choose)
    # -------------------------------------------------
    if step is None or step == "start":

        text = gpt_reply(
            history,
            """
Invite gently.
Ask what feels easier right now:
- Light movement
- Something sensory
- A simple mental task
""",
            spiral_stage
        )

        return {"step": "choose_type", "text": text}

    # -------------------------------------------------
    # STEP 1 — CHOOSE TYPE
    # -------------------------------------------------
    if step == "choose_type":

        activity_type = classify_activity_type(user_text)

        if activity_type == "MOVEMENT":
            instruction = """
Suggest one very light two-minute movement activity.
Keep it simple.
"""
        elif activity_type == "SENSORY":
            instruction = """
Suggest one gentle sensory activity.
Keep it grounding.
"""
        else:
            instruction = """
Suggest one simple mental task.
Very low effort.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "try_activity", "text": text}

    # -------------------------------------------------
    # STEP 2 — CHECK
    # -------------------------------------------------
    if step == "try_activity":

        text = gpt_reply(
            history,
            """
After the activity, ask:
"Did that shift anything, even slightly?"
Keep tone soft.
""",
            spiral_stage
        )

        return {"step": "check_mood", "text": text}

    # -------------------------------------------------
    # STEP 3 — MOOD CHECK
    # -------------------------------------------------
    if step == "check_mood":

        result = classify_shift(user_text)

        if result == "BETTER":

            text = gpt_reply(
                history,
                """
Acknowledge the small shift warmly.
Reinforce that even slight change counts.
Close gently.
""",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        if result == "SAME":

            text = gpt_reply(
                history,
                """
Normalize that sometimes the first activity doesn’t shift much.
Ask gently if they'd like to try one different small activity.
""",
                spiral_stage
            )

            return {"step": "retry_permission", "text": text}

        if result == "WORSE":

            text = gpt_reply(
                history,
                """
Acknowledge gently.
Suggest stopping.
Reassure it's okay if it didn’t help.
Close softly.
""",
                spiral_stage
            )

            return {"step": "exit", "text": text}

    # -------------------------------------------------
    # STEP 4 — RETRY
    # -------------------------------------------------
    if step == "retry_permission":

        decision = classify_yes_no(user_text)

        if decision == "YES":

            text = gpt_reply(
                history,
                """
Suggest a different small activity than before.
Keep it simple.
""",
                spiral_stage
            )

            return {"step": "try_activity", "text": text}

        text = gpt_reply(
            history,
            """
Reassure stopping anytime is okay.
Close gently.
""",
            spiral_stage
        )

        return {"step": "exit", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    return {"step": "exit", "text": "Pausing here is okay."}