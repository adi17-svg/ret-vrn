"""
Low Mood Tool: Gentle Distraction (Fully Stabilized)

Features:
- Smart start detection
- Spiral-aware tone (internal)
- Fallback defaults
- Low-confidence handling
- Safe activity fallback
- Mood-check stabilization
- Independent GPT usage
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
# SAFE CLASSIFIER WRAPPER
# =====================================================

def safe_classify(system_instruction: str, user_text: str, valid_options: list, default: str):

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


# =====================================================
# SPIRAL CLASSIFIER
# =====================================================

def classify_spiral(user_text: str) -> str:
    return safe_classify(
        "Classify into one word: BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW.",
        user_text,
        ["BEIGE", "PURPLE", "RED", "BLUE", "ORANGE", "GREEN", "YELLOW"],
        "GREEN"
    )


# =====================================================
# YES / NO
# =====================================================

def classify_yes_no(user_text: str) -> str:
    return safe_classify(
        "Classify into one word: YES, NO, or UNCLEAR.",
        user_text,
        ["YES", "NO", "UNCLEAR"],
        "UNCLEAR"
    )


# =====================================================
# ACTIVITY TYPE
# =====================================================

def classify_activity_type(user_text: str) -> str:
    return safe_classify(
        "Classify into one word: MOVEMENT, SENSORY, or MENTAL.",
        user_text,
        ["MOVEMENT", "SENSORY", "MENTAL"],
        "MENTAL"
    )


# =====================================================
# MOOD SHIFT
# =====================================================

def classify_shift(user_text: str) -> str:
    return safe_classify(
        "Classify into one word: BETTER, SAME, or WORSE.",
        user_text,
        ["BETTER", "SAME", "WORSE"],
        "SAME"
    )


# =====================================================
# GPT REPLY
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
    # STEP 0 — SMART START
    # -------------------------------------------------
    if step is None or step == "start":

        if user_text and any(word in user_text.lower() for word in [
            "yes", "sure", "okay", "distract", "something light", "let's"
        ]):
            text = gpt_reply(
                history,
                """
Acknowledge readiness.
Ask what kind of small activity feels easier:
- Light movement
- Sensory
- Something simple for the mind
""",
                spiral_stage
            )
            return {"step": "choose_type", "text": text}

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

    # -------------------------------------------------
    # STEP 1 — PERMISSION
    # -------------------------------------------------
    if step == "permission":

        decision = classify_yes_no(user_text)

        if decision == "YES":
            text = gpt_reply(
                history,
                """
Ask what kind of small activity feels easier right now:
- Light movement
- Sensory
- Something simple for the mind
""",
                spiral_stage
            )
            return {"step": "choose_type", "text": text}

        if decision == "NO":
            text = gpt_reply(
                history,
                "Acknowledge gently and reassure stopping is okay.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        # UNCLEAR fallback
        text = gpt_reply(
            history,
            "Gently ask if they'd like to try something small or just pause.",
            spiral_stage
        )
        return {"step": "permission", "text": text}

    # -------------------------------------------------
    # STEP 2 — ACTIVITY TYPE
    # -------------------------------------------------
    if step == "choose_type":

        activity_type = classify_activity_type(user_text)

        if activity_type == "MOVEMENT":
            instruction = "Suggest one very light two-minute movement activity."
        elif activity_type == "SENSORY":
            instruction = "Suggest one gentle sensory activity."
        else:
            instruction = "Suggest one simple mental activity."

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "try_activity", "text": text}

    # -------------------------------------------------
    # STEP 3 — AFTER ACTIVITY
    # -------------------------------------------------
    if step == "try_activity":

        text = gpt_reply(
            history,
            """
Ask gently:
"How do you feel now? Even slightly different, or about the same?"
""",
            spiral_stage
        )

        return {"step": "check_mood", "text": text}

    # -------------------------------------------------
    # STEP 4 — CHECK MOOD
    # -------------------------------------------------
    if step == "check_mood":

        result = classify_shift(user_text)

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
                "Normalize it’s okay if nothing changed. Offer trying one more small activity.",
                spiral_stage
            )
            return {"step": "retry_permission", "text": text}

        if result == "WORSE":
            text = gpt_reply(
                history,
                "Acknowledge gently and suggest stopping. Invite one slow breath.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

    # -------------------------------------------------
    # STEP 5 — RETRY
    # -------------------------------------------------
    if step == "retry_permission":

        decision = classify_yes_no(user_text)

        if decision == "YES":
            text = gpt_reply(
                history,
                "Suggest a different small activity.",
                spiral_stage
            )
            return {"step": "try_activity", "text": text}

        text = gpt_reply(
            history,
            "Reassure stopping anytime is okay. Close gently.",
            spiral_stage
        )
        return {"step": "exit", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    return {"step": "exit", "text": "Pausing here is okay."}
