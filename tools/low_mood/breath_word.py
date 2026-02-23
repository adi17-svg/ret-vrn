"""
Low Mood Tool: Breath Word
Conversational + Regulation → Integration Flow
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm breathing guide.

Rules:
- Keep responses short (2–4 lines)
- Gentle tone
- Clear guidance
- No analysis
- No advice
- Keep instructions simple
- After breathing, gently keep the conversation open
"""

# =====================================================
# SAFE CLASSIFIERS
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
# GPT REPLY (SAFE HISTORY MAPPING)
# =====================================================

def gpt_reply(history, instruction):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_BASE},
    ]

    if history:
        recent = history[-HISTORY_LIMIT:]

        for msg in recent:
            role = "assistant" if msg.get("type") == "assistant" else "user"
            content = msg.get("text", "")
            if content:
                messages.append({
                    "role": role,
                    "content": content
                })

    messages.append({
        "role": "user",
        "content": instruction
    })

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
    user_text = (user_text or "").strip()

    if not step:
        step = "start"

    # -------------------------------------------------
    # START
    # -------------------------------------------------

    if step == "start":

        text = gpt_reply(
            history,
            "Would it feel okay to take three slow breaths together?"
        )

        return {"step": "permission", "text": text}

    # -------------------------------------------------
    # PERMISSION
    # -------------------------------------------------

    if step == "permission":

        decision = classify_yes_no(user_text)

        if decision == "YES":

            text = gpt_reply(
                history,
                "Inhale slowly… and exhale gently."
            )

            return {"step": "cycle_2", "text": text}

        if decision == "NO":

            return {
                "step": "continue",
                "text": "That’s completely okay. We can simply stay here together."
            }

        text = gpt_reply(
            history,
            "Would you like to try just one slow breath instead?"
        )

        return {"step": "permission", "text": text}

    # -------------------------------------------------
    # BREATH CYCLE 2
    # -------------------------------------------------

    if step == "cycle_2":

        text = gpt_reply(
            history,
            "Again… inhale slowly… and exhale."
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
Inhale gently…
Exhale slowly…

Let your breath return to its own rhythm.
"""
        )

        return {"step": "notice", "text": text}

    # -------------------------------------------------
    # NOTICE AFTER BREATH
    # -------------------------------------------------

    if step == "notice":

        text = gpt_reply(
            history,
            "Now that your breath has slowed a little, what do you notice in your body?"
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
                "Even a small shift matters. What feels slightly different now?"
            )

        elif result == "NO_CHANGE":

            text = gpt_reply(
                history,
                "Sometimes breath simply creates a little space. What feels most present right now?"
            )

        else:

            text = gpt_reply(
                history,
                "Just noticing is enough. What stands out in your body at this moment?"
            )

        return {"step": "continue", "text": text}

    # -------------------------------------------------
    # CONTINUE MODE
    # -------------------------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}"\nRespond gently and stay with grounded awareness.'
        )

        return {"step": "continue", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "I’m here. What feels most present for you right now?"
    }