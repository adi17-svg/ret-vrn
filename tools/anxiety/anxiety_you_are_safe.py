# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Invite a brief pause.
# Reassure that in this moment, they are safe.
# Say nothing needs to be solved immediately.
# """
#         )
#     }
"""
Anxiety Tool: You Are Safe
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You provide present-moment safety reassurance.

Rules:
- Calm
- Slow
- No pressure
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
            "step": "land",
            "text": gpt_reply(user_text,
                              "Gently remind them that in this moment they are safe.")
        }

    return {
        "step": "exit",
        "text": gpt_reply(user_text,
                          "Invite letting that sense of safety settle.")
    }
