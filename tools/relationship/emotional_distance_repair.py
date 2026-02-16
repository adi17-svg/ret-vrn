from spiral_dynamics import client

SYSTEM_PROMPT = "Soften emotional shutdown gently."

def gpt_reply(u,i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":u or ""},
                  {"role":"assistant","content":i}],
        temperature=0.4).choices[0].message.content.strip()

def handle(step=None,user_text=None):

    if step is None:
        return {"step":"regulate","text":gpt_reply(user_text,"Notice if the body feels shut down or numb.")}

    if step=="regulate":
        return {"step":"clarify","text":gpt_reply(user_text,"What triggered the pull-away?")}

    if step=="clarify":
        return {"step":"insight","text":gpt_reply(user_text,"Explore if this is protection rather than indifference.")}

    if step=="insight":
        return {"step":"shift","text":gpt_reply(user_text,"Invite sharing one small honest feeling.")}

    if step=="shift":
        return {"step":"close","text":gpt_reply(user_text,"Connection can reopen gradually.")}

    return {"step":"exit","text":"Pause here."}
