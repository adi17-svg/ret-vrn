"""
Relationship Tool: Relationship Reality Check
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
Help differentiate fantasy from reality gently.

Rules:
- No harsh truth
- No partner judgment
- Encourage grounded observation
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
                "text":gpt_reply(user_text,"Slow down emotional intensity first.")}

    if step=="regulate":
        return {"step":"clarify",
                "text":gpt_reply(user_text,"What are you imagining about them?")}

    if step=="clarify":
        return {"step":"insight",
                "text":gpt_reply(user_text,"Compare imagination vs observable actions.")}

    if step=="insight":
        return {"step":"shift",
                "text":gpt_reply(user_text,"Invite grounding in facts, not hope or fear.")}

    if step=="shift":
        return {"step":"close",
                "text":gpt_reply(user_text,"Clarity prevents self-deception.")}

    return {"step":"exit","text":"Pause here."}
