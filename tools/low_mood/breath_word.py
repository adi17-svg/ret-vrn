"""
Low Mood Tool: Breath Word (Smooth Multi-Step Flow)

Design:
- Independent GPT usage
- Spiral-aware tone (internal only)
- Smart start detection
- 3 guided breath cycles (smooth rhythm)
- Gentle body noticing
- Soft containment close
- No loops
- No over-analysis
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


def classify_yes_no(user_text):
    return safe_classify(
        "Classify into one word: YES, NO, or UNCLEAR.",
        user_text,
        ["YES", "NO", "UNCLEAR"],
        "UNCLEAR"
    )


def classify_shift(user_text):
    return safe_classify(
        "Classify into one word: SUCCESS, NO_CHANGE, or UNCLEAR.",
        user_text,
        ["SUCCESS", "NO_CHANGE", "UNCLEAR"],
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

        if user_text and any(word in user_text.lower() for word in [
            "yes", "sure", "okay", "let's", "breathe"
        ]):
            text = gpt_reply(
                history,
                "Let’s begin. Inhale slowly — here. Exhale gently — now.",
                spiral_stage
            )
            return {"step": "cycle_2", "text": text}

        text = gpt_reply(
            history,
            "Would it feel okay to try three slow breaths together?",
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
                "Inhale slowly — here. Exhale gently — now.",
                spiral_stage
            )
            return {"step": "cycle_2", "text": text}

        if decision == "NO":
            return {
                "step": "exit",
                "text": "That's completely okay. We can pause here."
            }

        text = gpt_reply(
            history,
            "Would you like to try just one slow breath together?",
            spiral_stage
        )
        return {"step": "permission", "text": text}

    # -------------------------------------------------
    # BREATH CYCLE 2
    # -------------------------------------------------
    if step == "cycle_2":

        text = gpt_reply(
            history,
            "Again… Inhale — here. Exhale — now.",
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
One last time…
Inhale — here.
Exhale — now.

Let your breath return to its own rhythm.
""",
            spiral_stage
        )
        return {"step": "notice", "text": text}

    # -------------------------------------------------
    # GENTLE NOTICE
    # -------------------------------------------------
    if step == "notice":

        text = gpt_reply(
            history,
            "What do you notice in your body now?",
            spiral_stage
        )
        return {"step": "check_state", "text": text}

    # -------------------------------------------------
    # CHECK STATE
    # -------------------------------------------------
    if step == "check_state":

        result = classify_shift(user_text)

        if result == "SUCCESS":
            text = gpt_reply(
                history,
                "Even a small shift matters. Let’s pause here.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        if result == "NO_CHANGE":
            text = gpt_reply(
                history,
                "Sometimes breath just creates a little space. That’s enough for now.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        text = gpt_reply(
            history,
            "Just noticing is enough. We can pause here.",
            spiral_stage
        )
        return {"step": "exit", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    return {"step": "exit", "text": "We can pause here."}