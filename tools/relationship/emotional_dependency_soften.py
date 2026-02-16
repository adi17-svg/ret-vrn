"""
Relationship Tool: Emotional Dependency Soften
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
Help balance intense emotional dependency gently.

Rules:
- No shaming
- Strengthen self-anchor
- Encourage healthy independence
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
                "text":gpt_reply(user_text,"Notice the panic or intensity in your body.")}

    if step=="regulate":
        return {"step":"clarify",
                "text":gpt_reply(user_text,"What feels unbearable about being without them?")}

    if step=="clarify":
        return {"step":"insight",
                "text":gpt_reply(user_text,"Explore identity outside this relationship.")}

    if step=="insight":
        return {"step":"shift",
                "text":gpt_reply(user_text,"Anchor into one personal strength or value.")}

    if step=="shift":
        return {"step":"close",
                "text":gpt_reply(user_text,"Connection works best with two stable selves.")}

    return {"step":"exit","text":"Pause here."}
