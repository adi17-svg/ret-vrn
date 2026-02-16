"""
Relationship Tool: Boundaries in Love
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
Help maintain identity inside love.

Rules:
- No cold detachment
- Encourage healthy limits
"""

def gpt_reply(u,i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":u or ""},
            {"role":"assistant","content":i}],
        temperature=0.4).choices[0].message.content.strip()

def handle(step=None,user_text=None):

    if step is None:
        return {"step":"regulate",
                "text":gpt_reply(user_text,"Notice where you shrink to keep peace.")}

    if step=="regulate":
        return {"step":"clarify",
                "text":gpt_reply(user_text,"Where did you ignore your own need?")}

    if step=="clarify":
        return {"step":"insight",
                "text":gpt_reply(user_text,"Love does not require self-erasure.")}

    if step=="insight":
        return {"step":"shift",
                "text":gpt_reply(user_text,"Define one small boundary you can hold.")}

    if step=="shift":
        return {"step":"close",
                "text":gpt_reply(user_text,"Healthy love respects limits.")}

    return {"step":"exit","text":"Pause here."}
