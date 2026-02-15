# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "five",
#             "text": tool_gpt_reply(user_text, "Invite naming five things you can see.")
#         }

#     if step == "five":
#         return {
#             "step": "four",
#             "text": tool_gpt_reply(user_text, "Invite noticing four physical sensations.")
#         }

#     if step == "four":
#         return {
#             "step": "three",
#             "text": tool_gpt_reply(user_text, "Invite listening for three different sounds.")
#         }

#     if step == "three":
#         return {
#             "step": "two",
#             "text": tool_gpt_reply(user_text, "Invite noticing two smells.")
#         }

#     if step == "two":
#         return {
#             "step": "one",
#             "text": tool_gpt_reply(user_text, "Invite noticing one taste or pleasant sensation.")
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(
#             user_text,
#             "You’re here, in this moment. That’s enough."
#         )
#     }
"""
Low Mood Tool: 5-4-3-2-1 Grounding
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a grounding guide.

Rules:
- Calm tone
- Short steps
- No analysis
- Step-by-step only
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
        return {"step": "five",
                "text": gpt_reply(user_text, "Invite naming five things you can see.")}

    if step == "five":
        return {"step": "four",
                "text": gpt_reply(user_text, "Invite noticing four physical sensations.")}

    if step == "four":
        return {"step": "three",
                "text": gpt_reply(user_text, "Invite listening for three sounds.")}

    if step == "three":
        return {"step": "two",
                "text": gpt_reply(user_text, "Invite noticing two smells.")}

    if step == "two":
        return {"step": "one",
                "text": gpt_reply(user_text, "Invite noticing one taste or pleasant sensation.")}

    return {"step": "exit",
            "text": gpt_reply(user_text, "You’re here. That’s enough for now.")}
