"""
Relationship Tool: People-Pleasing Interrupt
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You help someone pause automatic people-pleasing.

Rules:
- Calm tone
- No blaming
- Encourage awareness before action
"""

def gpt_reply(u, i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":u or ""},
            {"role":"assistant","content":i}],
        temperature=0.4).choices[0].message.content.strip()

def handle(step=None, user_text=None):

    if step is None:
        return {"step":"regulate","text":gpt_reply(user_text,"Guide one slow breath before responding to anyone.")}

    if step=="regulate":
        return {"step":"clarify","text":gpt_reply(user_text,"Ask: did you say yes from choice or fear of rejection?")}

    if step=="clarify":
        return {"step":"insight","text":gpt_reply(user_text,"Help them notice the cost of automatic yes.")}

    if step=="insight":
        return {"step":"shift","text":gpt_reply(user_text,"Invite practicing one gentle pause before agreeing.")}

    if step=="shift":
        return {"step":"close","text":gpt_reply(user_text,"Reassure that boundaries don’t equal rejection.")}

    return {"step":"exit","text":"Pause here."}
