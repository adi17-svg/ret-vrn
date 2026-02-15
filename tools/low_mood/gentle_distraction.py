# from .tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "choose",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Gently suggest a neutral, low-effort activity they could do for a couple of minutes."
#             )
#         }

#     if step == "choose":
#         return {
#             "step": "exit",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Reassure them they can stop anytime and don’t need to do more."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(user_text, "Pausing here is okay.")
#     }
"""
Low Mood Tool: Gentle Distraction
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You suggest small neutral distractions.

Rules:
- Gentle tone
- No pressure
- Keep it simple
- No deep analysis
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
        temperature=0.5,
    )

    return resp.choices[0].message.content.strip()


def handle(step, user_text):

    if step is None or step == "start":
        return {
            "step": "choose",
            "text": gpt_reply(
                user_text,
                "Suggest one neutral, low-effort activity they could try for two minutes."
            )
        }

    if step == "choose":
        return {
            "step": "exit",
            "text": gpt_reply(
                user_text,
                "Reassure them they can stop anytime and don’t need to do more."
            )
        }

    return {"step": "exit", "text": "Pausing here is okay."}
