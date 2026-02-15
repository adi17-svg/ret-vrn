"""
Sleep Tool: Mind Unload
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You guide mental unloading before sleep.

Rules:
- Calm tone
- No analysis
- No solving
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
            "step": "unload",
            "text": gpt_reply(
                user_text,
                "Invite placing any remaining thoughts down for the night."
            )
        }

    if step == "unload":
        return {
            "step": "settle",
            "text": gpt_reply(
                user_text,
                "Encourage imagining them safely waiting for tomorrow."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Nothing needs to be solved right now."
        )
    }
