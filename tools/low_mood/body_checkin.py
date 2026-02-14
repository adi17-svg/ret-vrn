"""
Low Mood Tool: Body Check-In

Purpose:
- Increase somatic awareness
- Gently release physical tension
- No pushing, no fixing
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm, grounding mental health guide.

Rules:
- Keep responses short (1–3 lines)
- Speak gently
- No advice
- No analysis
- Just guide awareness
"""

def gpt_reply(user_text: str | None, instruction: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text or ""},
        {"role": "assistant", "content": instruction}
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


def handle(step: str | None, user_text: str | None):

    # STEP 1 — SCAN
    if step is None or step == "start":
        text = gpt_reply(
            user_text,
            """
Invite them to notice their shoulders, jaw, and hands.
No changing. Just noticing.
"""
        )
        return {"step": "scan", "text": text}

    # STEP 2 — RELEASE
    if step == "scan":
        text = gpt_reply(
            user_text,
            """
Invite softening just one area slightly, if it feels okay.
No pressure.
"""
        )
        return {"step": "release", "text": text}

    # STEP 3 — CLOSE
    if step == "release":
        text = gpt_reply(
            user_text,
            """
Close gently.
Remind them they don’t need to do more.
"""
        )
        return {"step": "exit", "text": text}

    return {
        "step": "exit",
        "text": "We can pause here."
    }
