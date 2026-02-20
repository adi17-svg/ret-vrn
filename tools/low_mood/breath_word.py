"""
Low Mood Tool: Breath Word (Fully Stabilized)

Features:
- Smart start detection
- Spiral-aware tone (internal only)
- Safe classifier wrapper
- Fallback defaults
- Low-confidence handling
- No loops
- Independent GPT usage
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

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
        temperature=0.3,
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

        # If user already ready
        if user_text and any(word in user_text.lower() for word in [
            "yes", "sure", "okay", "let's", "breathe"
        ]):
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

    # -------------------------------------------------
    # STEP 1 — PERMISSION
    # -------------------------------------------------
    if step == "permission":

        decision = classify_yes_no(user_text)

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
Close softly.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        # UNCLEAR fallback
        text = gpt_reply(
            history,
            "Gently ask if they'd prefer to breathe together or just pause.",
            spiral_stage
        )
        return {"step": "permission", "text": text}

    # -------------------------------------------------
    # BREATH CYCLE 2
    # -------------------------------------------------
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

    # -------------------------------------------------
    # BREATH CYCLE 3
    # -------------------------------------------------
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

    # -------------------------------------------------
    # CHECK STATE (SAFE RESPONSE)
    # -------------------------------------------------
    if step == "check_state":

        text = gpt_reply(
            history,
            f"""
User said: "{user_text}"

If calmer, affirm.
If same, normalize.
If unsure, gently reassure.
Close softly.
""",
            spiral_stage
        )
        return {"step": "exit", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    return {"step": "exit", "text": "We can pause here."}
