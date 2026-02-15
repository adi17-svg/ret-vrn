# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "vent",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Invite sharing freely here. No fixing. No judging."
#             )
#         }

#     if step == "vent":
#         return {
#             "step": "contain",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Thank them for letting it out."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(
#             user_text,
#             "You don’t have to solve anything right now."
#         )
#     }
"""
Low Mood Tool: Venting
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You hold space for emotional release.

Rules:
- No fixing
- No advice
- Just listening
- Warm tone
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
        temperature=0.6,
    )

    return resp.choices[0].message.content.strip()


def handle(step, user_text):

    if step is None or step == "start":
        return {
            "step": "vent",
            "text": gpt_reply(
                user_text,
                "Invite them to share freely. No fixing. No judging."
            )
        }

    if step == "vent":
        return {
            "step": "exit",
            "text": gpt_reply(
                user_text,
                "Thank them for sharing and gently close."
            )
        }

    return {"step": "exit", "text": "You don’t have to solve anything right now."}
