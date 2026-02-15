# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "name",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Invite them to name what this feeling is like, without explaining or analyzing it."
#             )
#         }

#     if step == "name":
#         return {
#             "step": "exit",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Reassure them that naming it is enough for now."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(user_text, "We can pause here.")
#     }
"""
Low Mood Tool: Name The Feeling
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You guide emotional labeling gently.

Rules:
- No analysis
- No advice
- Just naming
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
            "step": "name",
            "text": gpt_reply(
                user_text,
                "Invite them to name what this feeling is like, without explaining or analyzing it."
            )
        }

    if step == "name":
        return {
            "step": "exit",
            "text": gpt_reply(
                user_text,
                "Reassure them that naming it is enough for now."
            )
        }

    return {"step": "exit", "text": "We can pause here."}
