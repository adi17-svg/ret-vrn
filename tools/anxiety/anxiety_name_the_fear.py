# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Invite gently naming the fear in a few simple words.
# No explanation or fixing.
# Explain that naming alone can soften its intensity.
# """
#         )
#     }
"""
Anxiety Tool: Name The Fear
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You guide fear labeling gently.

Rules:
- No analysis
- No fixing
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
            "text": gpt_reply(user_text,
                              "Invite gently naming the fear in a few words.")
        }

    return {
        "step": "exit",
        "text": gpt_reply(user_text,
                          "Acknowledge that naming it is enough for now.")
    }
