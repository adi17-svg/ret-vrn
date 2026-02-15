# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Explain that not every worry needs attention right now.
# Offer the phrase “not now, I’ll come back later.”
# Encourage returning attention to the present moment.
# """
#         )
#     }
"""
Anxiety Tool: Not Now
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You reduce worry overload.

Rules:
- Gentle tone
- No solving
- Encourage containment
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
            "step": "contain",
            "text": gpt_reply(
                user_text,
                "Invite gently saying: 'Not now. I’ll come back to this later.'"
            )
        }

    if step == "contain":
        return {
            "step": "anchor",
            "text": gpt_reply(
                user_text,
                "Encourage returning attention to the present moment."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "That’s enough for now."
        )
    }
