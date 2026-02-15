# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "name",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Invite them to name one thing they don’t need to decide right now."
#             )
#         }

#     if step == "name":
#         return {
#             "step": "exit",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Remind them they can come back to that decision later."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(user_text, "Stopping here is okay.")
#     }
"""
Low Mood Tool: No Decision Now
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You reduce decision pressure gently.

Rules:
- No solving
- No pushing
- Light reassurance
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
            "step": "name",
            "text": gpt_reply(
                user_text,
                "Invite them to name one thing they don’t need to decide right now."
            )
        }

    if step == "name":
        return {
            "step": "exit",
            "text": gpt_reply(
                user_text,
                "Remind them they can return to that decision later."
            )
        }

    return {"step": "exit", "text": "Stopping here is okay."}
