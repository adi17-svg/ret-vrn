# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "identify",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Invite naming one thing that feels safe right now."
#             )
#         }

#     if step == "identify":
#         return {
#             "step": "focus",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Invite resting attention there briefly."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(
#             user_text,
#             "You’re safe in this moment."
#         )
#     }
"""
Low Mood Tool: One Safe Thing
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You guide safety anchoring.

Rules:
- Calm tone
- No fixing
- Just grounding
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
            "step": "identify",
            "text": gpt_reply(
                user_text,
                "Invite naming one thing that feels safe right now."
            )
        }

    if step == "identify":
        return {
            "step": "exit",
            "text": gpt_reply(
                user_text,
                "Invite resting attention there briefly."
            )
        }

    return {"step": "exit", "text": "You’re safe in this moment."}
