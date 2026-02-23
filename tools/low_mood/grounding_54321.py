"""
Low Mood Tool: 5-4-3-2-1 Grounding
Regulation + Soft Bridge Version
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm grounding guide.

Rules:
- Calm tone
- Short instructions
- Step-by-step only
- No analysis
- No therapy explanations
- Keep language simple
- When closing, gently reopen space for reflection
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


def classify_state_response(user_text):
    return safe_classify(
        "Classify into one word: CALMER, SAME, or UNSETTLED.",
        user_text,
        ["CALMER", "SAME", "UNSETTLED"],
        "SAME"
    )


# =====================================================
# GPT REPLY (History Aware)
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

    # =================================================
    # PERMISSION
    # =================================================

    if step == "start":

        text = gpt_reply(
            history,
            "Would it feel okay to try a short grounding exercise together?"
        )

        return {"step": "permission", "text": text}

    if step == "permission":

        if user_text.lower() not in ["yes", "yeah", "ok", "okay", "sure"]:

            return {
                "step": "exit",
                "text": "That’s completely okay. If you’d like, we can talk about what’s coming up instead."
            }

        text = gpt_reply(
            history,
            "Let’s begin. Name 5 things you can see around you."
        )

        return {"step": "five", "text": text}

    # =================================================
    # 5 → 4 → 3 → 2 → 1
    # =================================================

    if step == "five":

        text = gpt_reply(
            history,
            "Good. Now notice 4 physical sensations — what you can feel right now."
        )

        return {"step": "four", "text": text}

    if step == "four":

        text = gpt_reply(
            history,
            "Now listen for 3 different sounds around you."
        )

        return {"step": "three", "text": text}

    if step == "three":

        text = gpt_reply(
            history,
            "Notice 2 smells. If you can’t find any, that’s okay."
        )

        return {"step": "two", "text": text}

    if step == "two":

        text = gpt_reply(
            history,
            "Finally, notice 1 taste or small pleasant sensation."
        )

        return {"step": "one", "text": text}

    # =================================================
    # CHECK STATE
    # =================================================

    if step == "one":

        text = gpt_reply(
            history,
            "Take a slow breath. How does your body feel now?"
        )

        return {"step": "check", "text": text}

    if step == "check":

        state = classify_state_response(user_text)

        if state == "CALMER":

            text = gpt_reply(
                history,
                """
Even a small sense of steadiness matters.

We can gently pause here —
or, if you’d like, we can explore what was feeling heavy.
"""
            )

            return {"step": "exit", "text": text}

        if state == "UNSETTLED":

            text = gpt_reply(
                history,
                """
Thank you for staying with it.

Let’s take one slow breath together.
If you'd like, we can talk about what’s still unsettled.
"""
            )

            return {"step": "exit", "text": text}

        text = gpt_reply(
            history,
            """
Sometimes grounding works quietly.

You’re here.
If you'd like, we can gently continue.
"""
        )

        return {"step": "exit", "text": text}

    # =================================================
    # FALLBACK
    # =================================================

    return {
        "step": "exit",
        "text": "You’re here. That matters."
    }