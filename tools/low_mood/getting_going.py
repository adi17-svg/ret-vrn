"""
Low Mood Tool: Getting Going With Action (FINAL – RETVRN Version)

Flow:
1. Detect struggle
2. Spiral detect (background)
3. Validate
4. Ask blocker
5. Suggest tiny step (spiral-based)
6. Permission gate
7. Do
8. Close

Design principles:
- GPT used for tone only
- Tool controls flow strictly
- Spiral runs silently
- No looping
- Permission-based action
"""

from spiral_dynamics import client


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
You are a calm, supportive mental health coach.

Rules:
- Keep responses short (2–4 lines)
- Sound natural and human
- Never command harshly
- Use permission before action
- Once user agrees, STOP asking questions
- Guide action clearly and simply
- Respect resistance
"""


# =========================
# GPT HELPER
# =========================

def gpt_reply(user_text: str | None, instruction: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text or ""},
        {"role": "assistant", "content": instruction}
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.3,
    )

    return resp.choices[0].message.content.strip()


# =========================
# STRUGGLE DETECTION
# =========================

def looks_like_struggle(text: str | None) -> bool:
    if not text:
        return False

    keywords = [
        "hard", "can't", "cannot", "difficult",
        "lazy", "stuck", "tired", "avoid",
        "procrastinate", "low", "no energy"
    ]

    return any(k in text.lower() for k in keywords)


# =========================
# SPIRAL DETECTION (BACKGROUND)
# =========================

def detect_spiral_stage(text: str | None) -> str:
    if not text:
        return "Neutral"

    prompt = f"""
Classify the emotional tone into one:

Blue – structure, guilt, responsibility
Red – resistance, impulse, anger
Orange – achievement pressure, productivity stress
Green – emotional overwhelm, meaning focus
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


# =========================
# MAIN HANDLER
# =========================

def handle(step: str | None, user_text: str | None, memory: dict | None = None):

    memory = memory or {}

    # -------------------------
    # STEP 0 — INTRO / BANNER SAFE
    # -------------------------
    if step is None or step == "start":

        text = gpt_reply(
            user_text,
            """
Normalize low energy gently.
Explain we’ll take one small step.
Ask what feels hardest to start right now.
"""
        )

        return {"step": "ack", "text": text, "memory": memory}

    # -------------------------
    # STEP 1 — DETECT STRUGGLE
    # -------------------------
    if step == "ack":

        if not looks_like_struggle(user_text):
            text = gpt_reply(
                user_text,
                """
Respond supportively.
Gently invite them to share something that feels hard to start.
Keep it open.
"""
            )
            return {"step": "ack", "text": text, "memory": memory}

        # Spiral detection
        stage = detect_spiral_stage(user_text)
        memory["spiral_stage"] = stage
        memory["struggle"] = user_text

        text = gpt_reply(
            user_text,
            """
Briefly validate what they shared.
Then gently ask:
"What feels like it's getting in the way?"
Keep it short.
"""
        )

        return {"step": "blocker", "text": text, "memory": memory}

    # -------------------------
    # STEP 2 — ASK BLOCKER
    # -------------------------
    if step == "blocker":

        memory["blocker"] = user_text
        stage = memory.get("spiral_stage", "Neutral")

        instruction = f"""
Based on spiral stage: {stage}

Offer ONE very small action (max 30 seconds).

Blue → structured mini step.
Red → quick challenge.
Orange → measurable mini-task.
Green → gentle emotional step.
Neutral → simple action.

Ask permission gently (one question only).
"""

        text = gpt_reply(user_text, instruction)

        return {"step": "consent", "text": text, "memory": memory}

    # -------------------------
    # STEP 3 — CONSENT GATE
    # -------------------------
    if step == "consent":

        if user_text and user_text.lower().strip() in [
            "yes", "yeah", "yep", "ok", "okay",
            "sure", "let's try", "i will try"
        ]:
            text = gpt_reply(
                user_text,
                """
Acknowledge their willingness.
Say we’ll start now.
No questions.
"""
            )
            return {"step": "do", "text": text, "memory": memory}

        else:
            text = gpt_reply(
                user_text,
                """
Normalize hesitation.
Reassure that pausing is okay.
Close gently.
"""
            )
            return {"step": "close", "text": text, "memory": memory}

    # -------------------------
    # STEP 4 — DO ACTION
    # -------------------------
    if step == "do":

        text = gpt_reply(
            user_text,
            """
Guide one simple action clearly.
No questions.
Short instructions.
Example:
"Let’s try this together.
Take one slow breath in…
And release it gently."
"""
        )

        return {"step": "close", "text": text, "memory": memory}

    # -------------------------
    # STEP 5 — CLOSE
    # -------------------------
    if step == "close":

        text = gpt_reply(
            user_text,
            """
Close warmly.
Reinforce effort.
End clearly.
"""
        )

        return {"step": "exit", "text": text, "memory": memory}

    # -------------------------
    # SAFETY FALLBACK
    # -------------------------
    return {
        "step": "exit",
        "text": "We can pause here. You're in control.",
        "memory": memory
    }