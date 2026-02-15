"""
Sleep Tool: Nighttime Safety Anchor
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You reassure safety at night.

Rules:
- Gentle
- Slow pacing
- No analysis
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
        temperature=0.3,
    )

    return resp.choices[0].message.content.strip()


def handle(step=None, user_text=None):

    if step is None or step == "start":
        return {
            "step": "reassure",
            "text": gpt_reply(
                user_text,
                "Remind gently that this moment is safe."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Nothing needs your attention right now."
        )
    }
