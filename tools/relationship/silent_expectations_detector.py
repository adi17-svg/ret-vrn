from spiral_dynamics import client

SYSTEM_PROMPT = "Help uncover unspoken expectations gently."

def gpt_reply(u,i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":u or ""},
                  {"role":"assistant","content":i}],
        temperature=0.4).choices[0].message.content.strip()

def handle(step=None,user_text=None):

    if step is None:
        return {"step":"regulate","text":gpt_reply(user_text,"Slow the reaction before analyzing it.")}

    if step=="regulate":
        return {"step":"clarify","text":gpt_reply(user_text,"What were you hoping they would do without you saying it?")}

    if step=="clarify":
        return {"step":"insight","text":gpt_reply(user_text,"Help notice expectation vs communication.")}

    if step=="insight":
        return {"step":"shift","text":gpt_reply(user_text,"Invite expressing one need clearly next time.")}

    if step=="shift":
        return {"step":"close","text":gpt_reply(user_text,"Clarity reduces resentment.")}

    return {"step":"exit","text":"Pause here."}
