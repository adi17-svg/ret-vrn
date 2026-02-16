from spiral_dynamics import client

SYSTEM_PROMPT = "Help release resentment safely."

def gpt_reply(u,i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":u or ""},
                  {"role":"assistant","content":i}],
        temperature=0.4).choices[0].message.content.strip()

def handle(step=None,user_text=None):

    if step is None:
        return {"step":"regulate","text":gpt_reply(user_text,"Slow the anger before exploring it.")}

    if step=="regulate":
        return {"step":"clarify","text":gpt_reply(user_text,"What hurt was never expressed?")}

    if step=="clarify":
        return {"step":"insight","text":gpt_reply(user_text,"Resentment often hides unmet needs.")}

    if step=="insight":
        return {"step":"shift","text":gpt_reply(user_text,"Invite safe expression or journaling.")}

    if step=="shift":
        return {"step":"close","text":gpt_reply(user_text,"Let the emotional charge reduce.")}

    return {"step":"exit","text":"Pause here."}
