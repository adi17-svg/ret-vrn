"""
Sleep Tool: Morning Damage Control
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You help reduce morning anxiety after poor sleep.

Rules:
- No catastrophizing
- Gentle reassurance
- Practical calm tone
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
            "step": "reframe",
            "text": gpt_reply(
                user_text,
                "Reassure that one bad night doesn’t ruin the whole day."
            )
        }

    if step == "reframe":
        return {
            "step": "focus",
            "text": gpt_reply(
                user_text,
                "Invite focusing on just the next small task."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "The day can still unfold gently."
        )
    }
