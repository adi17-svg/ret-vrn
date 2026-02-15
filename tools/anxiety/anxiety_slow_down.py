# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Reassure that slowing down is allowed.
# Say there is no need to rush this moment.
# Invite the body to move at a gentler pace.
# """
#         )
#     }
"""
Anxiety Tool: Slow Down
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You allow slowing down safely.

Rules:
- Reassuring
- No urgency
- Gentle pacing
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


def handle(step, user_text):

    if step is None or step == "start":
        return {
            "step": "permission",
            "text": gpt_reply(
                user_text,
                "Give permission to slow down and move at a gentler pace."
            )
        }

    if step == "permission":
        return {
            "step": "settle",
            "text": gpt_reply(
                user_text,
                "Invite letting the body move a little slower."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "That’s enough for this moment."
        )
    }
