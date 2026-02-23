"""
Low Mood Tool: Getting Going With Action
RETVRN Conversational Version
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6


# ======================================
# SYSTEM PROMPT
# ======================================

SYSTEM_PROMPT = """
You are a calm, supportive mental health coach.

Rules:
- Keep responses short (2–4 lines)
- Sound natural and human
- Move gradually toward small action
- Never rush into advice
- Reinforce small steps
- Stay aligned with: "Start small. No pressure."
- After suggesting action, gently keep conversation open
"""


# ======================================
# GPT HELPER (History Aware + Correct Roles)
# ======================================

def gpt_reply(history, instruction):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Safe history mapping (last 6)
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

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


# ======================================
# STRUGGLE DETECTION
# ======================================

def looks_like_struggle(text):

    if not text:
        return False

    keywords = [
        "hard", "can't", "cannot", "difficult",
        "stuck", "lazy", "tired", "avoid",
        "procrastinate", "low", "no energy",
        "heavy", "overwhelmed"
    ]

    return any(k in text.lower() for k in keywords)


# ======================================
# SPIRAL DETECTION (Background Only)
# ======================================

def detect_spiral_stage(text):

    if not text:
        return "Neutral"

    prompt = f"""
Classify emotional tone into one:

Blue – guilt, responsibility focus
Red – resistance, frustration
Orange – productivity pressure
Green – emotional overwhelm
Neutral – unclear

Message: {text}

Return only one word.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# ======================================
# MICRO ACTION BASED ON SPIRAL
# ======================================

def get_micro_action(stage):

    if stage == "Blue":
        return "Set a 2-minute timer and simply sit with the task in front of you."

    if stage == "Red":
        return "Give yourself a 60-second challenge — just begin, no thinking."

    if stage == "Orange":
        return "Complete one very small measurable piece — just the first step."

    if stage == "Green":
        return "Take one slow breath and gently start the smallest possible part."

    return "Begin with the smallest possible action — nothing more."


# ======================================
# MAIN HANDLER
# ======================================

def handle(step=None, user_text=None, history=None, memory=None):

    history = history or []
    memory = memory or {}
    user_text = (user_text or "").strip()

    if not step:
        step = "start"

    # ----------------------------------
    # STEP 0 — INTRO
    # ----------------------------------

    if step == "start":

        text = gpt_reply(
            history,
            "Low energy happens. We’ll take just one small step. What feels hardest to begin right now?"
        )

        return {"step": "ack", "text": text, "memory": memory}

    # ----------------------------------
    # STEP 1 — DETECT STRUGGLE
    # ----------------------------------

    if step == "ack":

        if not looks_like_struggle(user_text):

            text = gpt_reply(
                history,
                "Tell me something that feels hard to start. We’ll keep it light."
            )

            return {"step": "ack", "text": text, "memory": memory}

        stage = detect_spiral_stage(user_text)
        memory["spiral_stage"] = stage
        memory["struggle"] = user_text

        text = gpt_reply(
            history,
            """
That sounds heavy.
When you think about starting,
is it more low energy, distraction, or pressure?
"""
        )

        return {"step": "blocker", "text": text, "memory": memory}

    # ----------------------------------
    # STEP 2 — BLOCKER EXPLORE
    # ----------------------------------

    if step == "blocker":

        memory["blocker"] = user_text

        text = gpt_reply(
            history,
            "I hear that. Would you like to try a very small experiment?"
        )

        return {"step": "permission", "text": text, "memory": memory}

    # ----------------------------------
    # STEP 3 — PERMISSION
    # ----------------------------------

    if step == "permission":

        if user_text.lower() in ["yes", "yeah", "yep", "ok", "okay", "sure", "let's", "i'll try"]:

            stage = memory.get("spiral_stage", "Neutral")
            micro_action = get_micro_action(stage)

            text = gpt_reply(
                history,
                f"""
Let’s keep it small.

Try this:
{micro_action}

No pressure.
"""
            )

            return {"step": "integrate", "text": text, "memory": memory}

        text = gpt_reply(
            history,
            "That’s okay. No pressure at all. What feels manageable right now?"
        )

        return {"step": "continue", "text": text, "memory": memory}

    # ----------------------------------
    # STEP 4 — INTEGRATE
    # ----------------------------------

    if step == "integrate":

        text = gpt_reply(
            history,
            "Even considering change counts. What feels possible from here?"
        )

        return {"step": "continue", "text": text, "memory": memory}

    # ----------------------------------
    # CONTINUE MODE
    # ----------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}"\nRespond supportively and stay aligned with small steps.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # ----------------------------------
    # FALLBACK
    # ----------------------------------

    return {
        "step": "continue",
        "text": "Start small. No pressure. What feels manageable right now?",
        "memory": memory
    }