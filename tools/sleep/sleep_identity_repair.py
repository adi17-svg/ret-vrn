"""
Sleep Tool: Sleep Identity Repair
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You help rebuild confidence around sleep.

Rules:
- Encouraging
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
            "step": "repair",
            "text": gpt_reply(
                user_text,
                "Reassure that struggling with sleep doesn’t define them."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Sleep patterns can change over time."
        )
    }
