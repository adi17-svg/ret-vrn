"""
Relationship Tool: Attachment Activation Check
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm attachment-aware relationship guide.

Rules:
- Short responses (2–4 lines)
- No partner blaming
- No advice-giving
- Help build awareness first
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

def handle(step=None, user_text=None):

    if step is None or step == "start":
        return {"step": "regulate",
                "text": gpt_reply(user_text,
                                  "Acknowledge activation and guide one slow breath.")}

    if step == "regulate":
        return {"step": "clarify",
                "text": gpt_reply(user_text,
                                  "Invite noticing: is this fear of losing them or hurt from something specific?")}

    if step == "clarify":
        return {"step": "insight",
                "text": gpt_reply(user_text,
                                  "Help differentiate attachment fear vs actual behavior.")}

    if step == "insight":
        return {"step": "shift",
                "text": gpt_reply(user_text,
                                  "Invite one grounded response instead of reactive texting or clinging.")}

    if step == "shift":
        return {"step": "close",
                "text": gpt_reply(user_text,
                                  "Reinforce that awareness reduces panic.")}

    return {"step": "exit", "text": "We can pause here."}
