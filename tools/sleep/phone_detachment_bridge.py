"""
Sleep Tool: Phone Detachment Bridge
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You gently help someone put their phone down before sleep.

Rules:
- No shame
- No pressure
- Gentle encouragement
"""

def gpt_reply(user_text, instruction):
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


def handle(step=None, user_text=None):

    if step is None or step == "start":
        return {
            "step": "bridge",
            "text": gpt_reply(
                user_text,
                "Gently acknowledge the pull of the phone."
            )
        }

    if step == "bridge":
        return {
            "step": "pause",
            "text": gpt_reply(
                user_text,
                "Invite placing the phone face down for a few minutes."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Even a small pause helps the brain wind down."
        )
    }
