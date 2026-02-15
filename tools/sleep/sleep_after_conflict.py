"""
Sleep Tool: Sleep After Conflict
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You help calm the nervous system after emotional conflict.

Rules:
- No analysis of the argument
- Gentle grounding
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
            "step": "settle",
            "text": gpt_reply(
                user_text,
                "Acknowledge that conflict can leave the body activated."
            )
        }

    if step == "settle":
        return {
            "step": "ground",
            "text": gpt_reply(
                user_text,
                "Guide one slow breath to help the body settle."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "The night can still be calm."
        )
    }
