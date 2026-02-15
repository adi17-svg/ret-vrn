# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "minimum",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Invite them to consider the absolute minimum that would be enough for today."
#             )
#         }

#     if step == "minimum":
#         return {
#             "step": "exit",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Affirm that this minimum is enough for now."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(user_text, "We can stop here.")
#     }
"""
Low Mood Tool: Lower The Bar
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You reduce pressure gently.

Rules:
- No pushing
- No advice
- Encourage minimum effort
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
            "step": "minimum",
            "text": gpt_reply(
                user_text,
                "Invite them to consider the absolute minimum that would be enough for today."
            )
        }

    if step == "minimum":
        return {
            "step": "exit",
            "text": gpt_reply(
                user_text,
                "Affirm that this minimum is enough for now."
            )
        }

    return {"step": "exit", "text": "We can stop here."}
