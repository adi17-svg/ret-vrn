from spiral_dynamics import client

SYSTEM_PROMPT = "Calm post-conflict regulator. No analysis. Settle the body."

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
        return {"step":"regulate","text":gpt_reply(user_text,"Guide slow breathing and unclenching jaw.")}

    if step=="regulate":
        return {"step":"clarify","text":gpt_reply(user_text,"Name what is still lingering: anger, hurt, or tension?")}

    if step=="clarify":
        return {"step":"insight","text":gpt_reply(user_text,"Separate current safety from past argument energy.")}

    if step=="insight":
        return {"step":"shift","text":gpt_reply(user_text,"Invite letting the body discharge the leftover activation.")}

    if step=="shift":
        return {"step":"close","text":gpt_reply(user_text,"Reassure conflict energy fades.")}

    return {"step":"exit","text":"Pause here."}
