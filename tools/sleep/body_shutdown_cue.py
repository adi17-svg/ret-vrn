"""
Sleep Tool: Body Shutdown Cue
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm nighttime wind-down guide.

Rules:
- Slow tone
- Short lines
- No forcing sleep
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
            "step": "soften",
            "text": gpt_reply(
                user_text,
                "Invite letting shoulders soften and jaw unclench gently."
            )
        }

    if step == "soften":
        return {
            "step": "slow_breath",
            "text": gpt_reply(
                user_text,
                "Guide one slow inhale and longer exhale."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Allow the body to power down naturally, without trying to sleep."
        )
    }
