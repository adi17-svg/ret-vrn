from spiral_dynamics import client

SYSTEM_PROMPT = "Differentiate intuition from fear."

def gpt_reply(u,i):
    return client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":u or ""},
                  {"role":"assistant","content":i}],
        temperature=0.4).choices[0].message.content.strip()

def handle(step=None,user_text=None):

    if step is None:
        return {"step":"regulate","text":gpt_reply(user_text,"Slow the nervous system first.")}

    if step=="regulate":
        return {"step":"clarify","text":gpt_reply(user_text,"Is this feeling coming from present evidence or past fear?")}

    if step=="clarify":
        return {"step":"insight","text":gpt_reply(user_text,"Separate trauma echo from current reality.")}

    if step=="insight":
        return {"step":"shift","text":gpt_reply(user_text,"Encourage grounded response instead of reactive move.")}

    if step=="shift":
        return {"step":"close","text":gpt_reply(user_text,"Awareness builds trust in yourself.")}

    return {"step":"exit","text":"Pause here."}
