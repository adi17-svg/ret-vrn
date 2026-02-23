"""
Low Mood Tool: Body Check-In
Conversational + Context Aware + No Abrupt Exit
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm, grounding mental health guide.

Rules:
- Keep responses short (2–4 lines)
- Gentle tone
- No advice
- No fixing
- No analysis
- Guide awareness simply
- Keep the conversation softly open
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
        temperature=0.4,
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
            "Would it feel okay to gently notice how your body feels right now?"
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
                "When things feel heavy, does your body feel tight, tired, or heavy anywhere?"
            )

            return {"step": "scan", "text": text}

        text = gpt_reply(
            history,
            "That's completely okay. Would taking one slow breath together feel easier?"
        )

        return {"step": "alt_option", "text": text}

    # -------------------------------------------------
    # ALT OPTION
    # -------------------------------------------------

    if step == "alt_option":

        decision = classify_yes_no(user_text)

        if decision == "YES":

            text = gpt_reply(
                history,
                "Let’s take one slow breath together. Inhale gently… and exhale slowly."
            )

            return {"step": "continue", "text": text}

        return {
            "step": "continue",
            "text": "That’s completely fine. We can simply stay here."
        }

    # -------------------------------------------------
    # SCAN
    # -------------------------------------------------

    if step == "scan":

        text = gpt_reply(
            history,
            f"""
User said: "{user_text}"

Acknowledge briefly.
Invite them to gently notice that area without trying to change it.
"""
        )

        return {"step": "soften", "text": text}

    # -------------------------------------------------
    # SOFTEN
    # -------------------------------------------------

    if step == "soften":

        text = gpt_reply(
            history,
            "If it feels okay, see if that area could soften just 5%. No forcing."
        )

        return {"step": "check", "text": text}

    # -------------------------------------------------
    # CHECK SHIFT
    # -------------------------------------------------

    if step == "check":

        result = classify_shift(user_text)

        if result == "SUCCESS":

            text = gpt_reply(
                history,
                "Acknowledge the small shift gently and ask what they notice now."
            )

        elif result == "NO_CHANGE":

            text = gpt_reply(
                history,
                "Acknowledge that nothing shifted and gently ask what feels most present now."
            )

        else:

            text = gpt_reply(
                history,
                "Affirm that simply noticing is enough and ask what stands out in the body now."
            )

        return {"step": "continue", "text": text}

    # -------------------------------------------------
    # CONTINUE MODE (Open Conversation)
    # -------------------------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}"\nRespond gently and stay with body awareness.'
        )

        return {"step": "continue", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "I'm here with you. What do you notice in your body right now?"
    }