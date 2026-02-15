"""
Sleep Tool: Late Night Overthinking Softener
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You gently soften late-night thinking.

Rules:
- Calm
- No problem-solving
- Encourage postponing thoughts
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
                "Acknowledge that thoughts feel louder at night."
            )
        }

    if step == "ack":
        return {
            "step": "contain",
            "text": gpt_reply(
                user_text,
                "Invite gently saying: 'Not tonight.'"
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Reassure nothing needs answers right now."
        )
    }
