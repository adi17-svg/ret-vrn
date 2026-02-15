"""
Sleep Tool: Can't Sleep Acceptance
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You normalize wakefulness at night.

Rules:
- No pressure
- Gentle reassurance
- No fixing
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
            "step": "normalize",
            "text": gpt_reply(
                user_text,
                "Normalize being awake right now."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Remind them that resting still helps the body."
        )
    }
