# from tool_gpt_anxiety import anxiety_gpt_reply

# def handle(step=None, user_text=None):
#     return {
#         "step": "exit",
#         "text": anxiety_gpt_reply(
#             user_text,
#             """
# Guide a slow breathing rhythm:
# inhale through the nose for four,
# hold gently for seven,
# exhale slowly through the mouth for eight.
# Keep the tone steady and calm.
# """
#         )
#     }
"""
Anxiety Tool: 4-7-8 Breathing
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm anxiety regulation guide.

Rules:
- Short instructions
- Clear pacing
- No analysis
- Guide step by step
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
            "step": "round1",
            "text": gpt_reply(user_text,
                              "Guide inhale 4, hold 7, exhale 8 slowly.")
        }

    if step == "round1":
        return {
            "step": "round2",
            "text": gpt_reply(user_text,
                              "Invite repeating once more gently.")
        }

    return {
        "step": "exit",
        "text": gpt_reply(user_text,
                          "Let the breath return to normal. That’s enough for now.")
    }
