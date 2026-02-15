# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Guide attention to physical contact.
# Mention feeling the chair, the floor, or the ground.
# Let the body notice support and stability.
# """
#         )
#     }
"""
Anxiety Tool: Grounding Through Touch
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You guide grounding through physical sensation.

Rules:
- Calm tone
- Concrete instructions
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


def handle(step, user_text):

    if step is None or step == "start":
        return {
            "step": "notice",
            "text": gpt_reply(
                user_text,
                "Invite noticing something they can physically touch — the chair, floor, or clothing."
            )
        }

    if step == "notice":
        return {
            "step": "stay",
            "text": gpt_reply(
                user_text,
                "Encourage staying with that sensation for a few breaths."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Remind them their body is supported right now."
        )
    }
