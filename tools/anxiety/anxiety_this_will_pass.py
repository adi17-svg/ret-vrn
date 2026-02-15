# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Reassure that anxiety is a temporary state, not permanent.
# Say it will change, even if slowly.
# Encourage patience without rushing the feeling away.
# """
#         )
#     }
"""
Anxiety Tool: This Will Pass
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You provide reassurance without minimizing.

Rules:
- Gentle
- No dismissing feelings
- Short reassurance
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
            "step": "reassure",
            "text": gpt_reply(
                user_text,
                "Acknowledge the intensity and gently remind that this state will shift."
            )
        }

    return {
        "step": "exit",
        "text": gpt_reply(
            user_text,
            "Encourage letting the feeling move at its own pace."
        )
    }
