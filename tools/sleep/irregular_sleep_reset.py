"""
Sleep Tool: Irregular Sleep Reset
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You normalize disrupted sleep patterns gently.

Rules:
- No blame
- No pressure
- Gentle reassurance
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
                "Normalize that sleep rhythms shift sometimes."
            )
        }

    if step == "normalize":
        return {
            "step": "gentle_reset",
            "text": gpt_reply(
                user_text,
                "Encourage small, gentle adjustments instead of drastic fixes."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Sleep can rebalance gradually."
        )
    }
