"""
Sleep Tool: Sleep Guilt Release
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You reduce guilt about sleep gently.

Rules:
- No shame
- No moral tone
- Just reassurance
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
            "step": "release",
            "text": gpt_reply(
                user_text,
                "Gently release guilt about how tonight is going."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Sleep is not something you can force."
        )
    }
