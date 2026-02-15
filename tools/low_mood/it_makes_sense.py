# from tool_gpt import tool_gpt_reply

# def handle(step: str | None, user_text: str | None):
#     if step in (None, "start"):
#         return {
#             "step": "validate",
#             "text": tool_gpt_reply(
#                 user_text,
#                 "Validate that their reaction makes sense given what they’re dealing with."
#             )
#         }

#     return {
#         "step": "exit",
#         "text": tool_gpt_reply(
#             user_text,
#             "They’re not overreacting."
#         )
#     }
"""
Low Mood Tool: It Makes Sense

Purpose:
- Validate emotional reactions
- Reduce shame
- No advice
- No fixing
"""

from spiral_dynamics import client


SYSTEM_PROMPT = """
You are a calm, validating mental health guide.

Rules:
- Keep responses short (1–3 lines)
- Warm and natural tone
- No advice
- No fixing
- Just validate gently
"""


def gpt_reply(user_text: str | None, instruction: str) -> str:
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


def handle(step: str | None, user_text: str | None):

    # STEP 1 — VALIDATE
    if step is None or step == "start":
        text = gpt_reply(
            user_text,
            """
Validate that their reaction makes sense given what they’re dealing with.
No analysis. No advice.
"""
        )
        return {"step": "exit", "text": text}

    # SAFETY FALLBACK
    return {
        "step": "exit",
        "text": "We can pause here."
    }
