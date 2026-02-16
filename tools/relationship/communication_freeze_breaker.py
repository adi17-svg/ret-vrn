"""
Relationship Tool: Communication Freeze Breaker
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You help someone safely unblock communication.

Rules:
- Calm tone
- No pressure to confront
- Build courage gradually
"""

def gpt_reply(u, i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": u or ""},
            {"role": "assistant", "content": i}
        ],
        temperature=0.4,
    ).choices[0].message.content.strip()


def handle(step=None, user_text=None):

    if step is None:
        return {"step": "regulate",
                "text": gpt_reply(user_text,
                                  "Notice the fear in your body before speaking.")}

    if step == "regulate":
        return {"step": "clarify",
                "text": gpt_reply(user_text,
                                  "What are you afraid will happen if you say it?")}

    if step == "clarify":
        return {"step": "insight",
                "text": gpt_reply(user_text,
                                  "Help separate imagined reaction from likely reality.")}

    if step == "insight":
        return {"step": "shift",
                "text": gpt_reply(user_text,
                                  "Draft one simple, calm sentence you could say.")}

    if step == "shift":
        return {"step": "close",
                "text": gpt_reply(user_text,
                                  "Courage grows with small attempts.")}

    return {"step": "exit", "text": "Pause here."}
