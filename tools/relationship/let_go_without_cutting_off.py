"""
Relationship Tool: Let Go Without Cutting Off
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
Teach emotional detachment without drama.

Rules:
- Mature tone
- No revenge mindset
- Encourage calm distance
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
                "text":gpt_reply(user_text,"Notice attachment energy before pulling away.")}

    if step=="regulate":
        return {"step":"clarify",
                "text":gpt_reply(user_text,"What are you trying to protect?")}

    if step=="clarify":
        return {"step":"insight",
                "text":gpt_reply(user_text,"Distance can be calm, not dramatic.")}

    if step=="insight":
        return {"step":"shift",
                "text":gpt_reply(user_text,"Choose quiet disengagement instead of reaction.")}

    if step=="shift":
        return {"step":"close",
                "text":gpt_reply(user_text,"Peace often comes from steady boundaries.")}

    return {"step":"exit","text":"Pause here."}
