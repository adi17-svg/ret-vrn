"""
Relationship Tool: Post-Argument Regulation
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You calm the nervous system after arguments.

Rules:
- No blame
- No analysis of the fight
- Focus on body regulation
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
        return {"step":"regulate",
                "text":gpt_reply(user_text,"Guide slow breathing and unclenching shoulders.")}

    if step=="regulate":
        return {"step":"clarify",
                "text":gpt_reply(user_text,"Notice what emotion is strongest right now.")}

    if step=="clarify":
        return {"step":"insight",
                "text":gpt_reply(user_text,"Remind that arguments activate survival mode.")}

    if step=="insight":
        return {"step":"shift",
                "text":gpt_reply(user_text,"Invite letting the body come out of fight mode.")}

    if step=="shift":
        return {"step":"close",
                "text":gpt_reply(user_text,"Conflict energy fades when not fed.")}

    return {"step":"exit","text":"Pause here."}
