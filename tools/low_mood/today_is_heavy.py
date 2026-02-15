# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "acknowledge",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Acknowledge that some days feel heavier than others."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(
#             user_text,
#             "You’re allowed to go slower today."
#         )
#     }
"""
Low Mood Tool: Today Is Heavy
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You validate heavy days.

Rules:
- No advice
- No pushing
- Gentle reassurance
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
            "step": "exit",
            "text": gpt_reply(
                user_text,
                "Acknowledge that some days feel heavier than others."
            )
        }

    return {"step": "exit", "text": "You’re allowed to go slower today."}
