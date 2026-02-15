# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Guide the eyes to rest on one neutral or gentle object.
# Avoid scanning the room.
# Encourage soft, relaxed focus for a few breaths.
# """
#         )
#     }
"""
Anxiety Tool: Soft Visual Focus
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You guide soft visual grounding.

Rules:
- Calm
- Simple instructions
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
            "step": "focus",
            "text": gpt_reply(
                user_text,
                "Invite resting eyes on one neutral object nearby."
            )
        }

    if step == "focus":
        return {
            "step": "stay",
            "text": gpt_reply(
                user_text,
                "Encourage staying with that visual focus for a few breaths."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "You can gently return to the room now."
        )
    }
