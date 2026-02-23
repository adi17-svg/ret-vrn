"""
Low Mood Tool: Gentle Distraction
Conversational + Context Aware + No Hard Exit
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6

# =====================================================
# SYSTEM PROMPT
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
- After activity, gently keep conversation open
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
        temperature=0.5,
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
    # STEP 0 — CHOOSE TYPE
    # -------------------------------------------------

    if step == "start":

        text = gpt_reply(
            history,
            """
Ask gently:
Would something light feel helpful right now?
You could choose:
- Light movement
- Something sensory
- A simple mental task
"""
        )

        return {"step": "choose_type", "text": text}

    # -------------------------------------------------
    # STEP 1 — SUGGEST ACTIVITY
    # -------------------------------------------------

    if step == "choose_type":

        activity_type = classify_activity_type(user_text)

        if activity_type == "MOVEMENT":
            instruction = "Suggest one very light two-minute movement activity."
        elif activity_type == "SENSORY":
            instruction = "Suggest one gentle sensory grounding activity."
        else:
            instruction = "Suggest one very simple low-effort mental task."

        text = gpt_reply(history, instruction)

        return {"step": "try_activity", "text": text}

    # -------------------------------------------------
    # STEP 2 — CHECK SHIFT
    # -------------------------------------------------

    if step == "try_activity":

        text = gpt_reply(
            history,
            "After trying that, did anything shift, even slightly?"
        )

        return {"step": "check_mood", "text": text}

    # -------------------------------------------------
    # STEP 3 — PROCESS RESPONSE
    # -------------------------------------------------

    if step == "check_mood":

        result = classify_shift(user_text)

        if result == "BETTER":

            text = gpt_reply(
                history,
                """
Acknowledge the small shift warmly.
Reinforce that even slight change matters.
Ask what feels different now.
"""
            )

            return {"step": "continue", "text": text}

        if result == "SAME":

            text = gpt_reply(
                history,
                """
Normalize that sometimes first attempts don't shift much.
Ask gently if they'd like to try something different,
or return to what was feeling heavy.
"""
            )

            return {"step": "retry_permission", "text": text}

        if result == "WORSE":

            text = gpt_reply(
                history,
                """
Acknowledge gently.
Reassure stopping is okay.
Ask what feels most supportive right now.
"""
            )

            return {"step": "continue", "text": text}

    # -------------------------------------------------
    # STEP 4 — RETRY OPTION
    # -------------------------------------------------

    if step == "retry_permission":

        decision = classify_yes_no(user_text)

        if decision == "YES":

            text = gpt_reply(
                history,
                "Suggest a different very small activity than before."
            )

            return {"step": "try_activity", "text": text}

        text = gpt_reply(
            history,
            "That’s okay. We don’t have to force anything. What feels most present now?"
        )

        return {"step": "continue", "text": text}

    # -------------------------------------------------
    # CONTINUE MODE
    # -------------------------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}"\nRespond gently and keep the conversation open.'
        )

        return {"step": "continue", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "I’m here. What feels most present for you right now?"
    }