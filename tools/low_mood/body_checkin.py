"""
Low Mood Tool: Body Check-In (Spiral + Gentle Resistance Handling)

Design:
- Independent GPT usage
- Spiral-aware tone (internal only)
- Permission asked once
- If NO → offer softer alternative
- Linear progression
- No looping permission
- Short, grounding responses
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm, grounding mental health guide.

Rules:
- Keep responses short (1–3 lines)
- Gentle tone
- No advice
- No analysis
- No fixing
- Guide awareness simply
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
        "Classify into one word: YES or NO.",
        user_text,
        ["YES", "NO"],
        "NO"
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
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []
    spiral_stage = classify_spiral(user_text) if user_text else "GREEN"

    # -------------------------------------------------
    # STEP 0 — START
    # -------------------------------------------------
    if step is None or step == "start":

        text = gpt_reply(
            history,
            "Would it feel okay to gently notice how your body feels right now?",
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
                "When you feel low like this, does your body feel heavy, tight, or tired anywhere?",
                spiral_stage
            )

            return {"step": "scan", "text": text}

        # If NO → Offer softer alternative
        text = gpt_reply(
            history,
            """
That's completely okay.
Would it feel easier to just take one slow breath together instead?
Only if you'd like.
""",
            spiral_stage
        )

        return {"step": "alt_option", "text": text}

    # -------------------------------------------------
    # STEP ALT OPTION (If they said NO)
    # -------------------------------------------------
    if step == "alt_option":

        decision = classify_yes_no(user_text)

        if decision == "YES":

            text = gpt_reply(
                history,
                "Let’s take one slow breath together. Inhale gently… and exhale slowly.",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        return {
            "step": "exit",
            "text": "That's completely fine. We can pause here."
        }

    # -------------------------------------------------
    # STEP 2 — SCAN
    # -------------------------------------------------
    if step == "scan":

        text = gpt_reply(
            history,
            f"""
User said: "{user_text}"

Briefly acknowledge.
Invite simply noticing that area for a few moments.
No changing.
""",
            spiral_stage
        )

        return {"step": "soften", "text": text}

    # -------------------------------------------------
    # STEP 3 — SOFTEN
    # -------------------------------------------------
    if step == "soften":

        text = gpt_reply(
            history,
            "If it feels okay, see if that area can soften just 5%.",
            spiral_stage
        )

        return {"step": "check", "text": text}

    # -------------------------------------------------
    # STEP 4 — CHECK SHIFT
    # -------------------------------------------------
    if step == "check":

        result = classify_shift(user_text)

        if result == "SUCCESS":

            text = gpt_reply(
                history,
                "That small shift matters. Let's stay with that for a moment.",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        if result == "NO_CHANGE":

            text = gpt_reply(
                history,
                "Sometimes nothing shifts right away. That's okay.",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        text = gpt_reply(
            history,
            "Even just noticing is enough for now.",
            spiral_stage
        )

        return {"step": "exit", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    return {"step": "exit", "text": "We can pause here."}