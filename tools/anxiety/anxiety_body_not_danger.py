# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Explain that anxiety can create strong body sensations like fast heartbeat
# or tight chest.
# Reassure that these sensations are uncomfortable but not dangerous.
# Say the body is trying to protect them.
# """
#         )
#     }
"""
Anxiety Tool: Body Is Not Danger
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You normalize anxiety sensations.

Rules:
- Reassuring tone
- No over-explaining
- Gentle validation
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
            "text": gpt_reply(user_text,
                              "Explain that anxiety sensations are uncomfortable but not dangerous.")
        }

    return {
        "step": "exit",
        "text": gpt_reply(user_text,
                          "Remind them their body is trying to protect them.")
    }
