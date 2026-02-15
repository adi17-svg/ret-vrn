# from .tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "breathe",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Guide a slow inhale with the word 'here' and exhale with 'now'."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(
#             user_text,
#             "Let the breath return to its own rhythm."
#         )
#     }
"""
Low Mood Tool: Breath Word
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm breathing guide.

Rules:
- Keep responses short
- Gentle tone
- Clear guidance
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
            "step": "breathe",
            "text": gpt_reply(
                user_text,
                "Guide a slow inhale with the word 'here' and exhale with 'now'."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Let the breath return to its natural rhythm."
        )
    }
