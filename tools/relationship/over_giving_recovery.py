from spiral_dynamics import client

SYSTEM_PROMPT = "Help restore balance after over-giving."

def gpt_reply(u,i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":u or ""},
                  {"role":"assistant","content":i}],
        temperature=0.4).choices[0].message.content.strip()

def handle(step=None,user_text=None):

    if step is None:
        return {"step":"regulate","text":gpt_reply(user_text,"Notice exhaustion in the body.")}

    if step=="regulate":
        return {"step":"clarify","text":gpt_reply(user_text,"What did you give beyond your limit?")}

    if step=="clarify":
        return {"step":"insight","text":gpt_reply(user_text,"Was it reciprocated or expected?")}

    if step=="insight":
        return {"step":"shift","text":gpt_reply(user_text,"Invite reclaiming one boundary.")}

    if step=="shift":
        return {"step":"close","text":gpt_reply(user_text,"Balance protects love.")}

    return {"step":"exit","text":"Pause here."}
