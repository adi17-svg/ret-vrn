# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Encourage letting the exhale be slightly longer than the inhale.
# No need to control the breath.
# Use slow, gentle language that reduces effort.
# """
#         )
#     }
"""
Anxiety Tool: Exhale Focus
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm breathing guide.

Rules:
- Short
- Gentle pacing
- No analysis
- Guide slowly
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
            "step": "extend",
            "text": gpt_reply(
                user_text,
                "Invite letting the exhale be slightly longer than the inhale."
            )
        }

    if step == "extend":
        return {
            "step": "settle",
            "text": gpt_reply(
                user_text,
                "Encourage repeating that gently for a few breaths."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Let the breath return to normal. That’s enough."
        )
    }
