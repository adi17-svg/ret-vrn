"""
Sleep Tool: Emotional Day Wind Down
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You gently help someone emotionally settle before sleep.

Rules:
- Calm tone
- No analysis
- No problem-solving
- Keep responses short
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
            "step": "ack",
            "text": gpt_reply(
                user_text,
                "Acknowledge that today carried emotions."
            )
        }

    if step == "ack":
        return {
            "step": "release",
            "text": gpt_reply(
                user_text,
                "Invite letting today gently close, without replaying it."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Remind that tomorrow can hold what’s unfinished."
        )
    }
