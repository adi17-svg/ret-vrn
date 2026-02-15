"""
Low Mood Tool: Body Check-In

Purpose:
- Increase somatic awareness
- Gently reconnect with the body
- Light release of tension
- No pushing, no fixing
"""

from spiral_dynamics import client


SYSTEM_PROMPT = """
You are a calm, grounding mental health guide.

Rules:
- Keep responses short (1–3 lines)
- Speak gently and naturally
- No advice
- No analysis
- No fixing
- Just guide awareness
"""


def gpt_reply(user_text: str | None, instruction: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text or ""},
        {"role": "assistant", "content": instruction},
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


def handle(step: str | None, user_text: str | None):

    # ==========================================
    # STEP 1 — OPENING BODY QUESTION
    # ==========================================
    if step is None or step == "start":
        text = gpt_reply(
            user_text,
            """
Ask gently:
"When you feel low like this, does your body feel heavy, tight, or tired anywhere?"
Keep it warm and simple.
"""
        )
        return {"step": "scan", "text": text}

    # ==========================================
    # STEP 2 — NOTICE (NO CHANGE YET)
    # ==========================================
    if step == "scan":
        text = gpt_reply(
            user_text,
            """
Briefly acknowledge what they shared.
Invite them to simply notice that area for a few seconds.
No changing. Just observing.
"""
        )
        return {"step": "release", "text": text}

    # ==========================================
    # STEP 3 — GENTLE SOFTENING
    # ==========================================
    if step == "release":
        text = gpt_reply(
            user_text,
            """
Invite softening that area just 5%, if it feels okay.
No pressure.
Close gently.
"""
        )
        return {"step": "exit", "text": text}

    # ==========================================
    # SAFETY FALLBACK
    # ==========================================
    return {
        "step": "exit",
        "text": "We can pause here."
    }
