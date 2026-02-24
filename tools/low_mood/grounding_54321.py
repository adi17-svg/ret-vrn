"""
Low Mood Tool: 5-4-3-2-1 Grounding
Adaptive Context Version (RETVRN v2)

Upgrades:
✔ Meaning extraction
✔ Blocker detection
✔ Spiral detection
✔ Context-aware state detection
✔ Spiral-aware micro step
✔ Direct progression toward action
✔ No repeated loops
✔ History-aware
✔ Natural flow
"""

from openai import OpenAI

client = OpenAI()
HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are a calm grounding guide.

Rules:
- Short responses (2–4 lines)
- Step-by-step only
- No therapy explanations
- Natural tone
- If calmer → gently move toward small action
- If unsettled → regulate once more, then bridge
- Never abruptly end
"""


# =====================================================
# GPT HELPER
# =====================================================

def gpt_reply(history, instruction):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[-HISTORY_LIMIT:]:
        role = "assistant" if msg.get("type") == "assistant" else "user"
        content = msg.get("text", "")
        if content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": instruction})

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# CONTEXT BUILDER
# =====================================================

def build_context(history, user_text):
    recent = " ".join([m.get("text", "") for m in history[-3:]])
    return f"{recent} {user_text}".strip()


# =====================================================
# SEMANTIC MEANING
# =====================================================

def extract_meaning(context):

    prompt = f"""
Summarize the person's core experience in 3–5 words.

Context:
"{context}"
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# BLOCKER DETECTION
# =====================================================

def detect_blocker(context):

    prompt = f"""
Classify main blocker:

INITIATION
OVERWHELM
DISTRACTION
LOW_ENERGY
FEAR
UNCLEAR

Context:
"{context}"

Return one word only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# SPIRAL DETECTION
# =====================================================

def detect_spiral(context):

    prompt = f"""
Classify tone into one:

BLUE
RED
ORANGE
GREEN
NEUTRAL

Context:
"{context}"

Return one word only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# STATE DETECTION AFTER GROUNDING
# =====================================================

def detect_state(context):

    prompt = f"""
After grounding, classify state:

CALMER
SAME
UNSETTLED
ACTION

Context:
"{context}"

Return one word only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# MICRO ACTION (SPIRAL-AWARE)
# =====================================================

def generate_micro_action(blocker, spiral):

    prompt = f"""
Blocker: {blocker}
Spiral tone: {spiral}

Generate one very small next step (5 minutes max).
Concrete.
No explanation.
One instruction only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None, memory=None):

    history = history or []
    memory = memory or {}
    user_text = (user_text or "").strip()

    if not step:
        step = "start"

    # -------------------------------------------------
    # START
    # -------------------------------------------------

    if step == "start":

        text = gpt_reply(
            history,
            "Would it feel okay to try a short grounding exercise together?"
        )

        return {"step": "permission", "text": text, "memory": memory}

    if step == "permission":

        if user_text.lower() not in ["yes", "yeah", "ok", "okay", "sure"]:

            return {
                "step": "bridge",
                "text": "That’s okay. We can gently talk about what feels heavy."
            }

        text = gpt_reply(
            history,
            "Name 5 things you can see around you."
        )

        return {"step": "five", "text": text, "memory": memory}

    # -------------------------------------------------
    # 5-4-3-2-1 FLOW
    # -------------------------------------------------

    if step == "five":
        return {"step": "four", "text": "Now notice 4 physical sensations.", "memory": memory}

    if step == "four":
        return {"step": "three", "text": "Listen for 3 different sounds.", "memory": memory}

    if step == "three":
        return {"step": "two", "text": "Notice 2 smells, if possible.", "memory": memory}

    if step == "two":
        return {"step": "one", "text": "Finally, notice 1 small pleasant sensation.", "memory": memory}

    if step == "one":
        return {"step": "check", "text": "Take one slow breath. How does your body feel now?", "memory": memory}

    # -------------------------------------------------
    # CHECK STATE
    # -------------------------------------------------

    if step == "check":

        context = build_context(history, user_text)
        state = detect_state(context)

        if state == "CALMER":

            meaning = extract_meaning(context)
            blocker = detect_blocker(context)
            spiral = detect_spiral(context)

            micro = generate_micro_action(blocker, spiral)

            text = gpt_reply(
                history,
                f"""
Good. Even a slight shift helps.

You mentioned {meaning}.

Try this small step:
{micro}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        if state == "UNSETTLED":

            text = gpt_reply(
                history,
                """
Okay. Let’s take one slow breath again.

Then tell me what still feels strongest.
"""
            )

            return {"step": "bridge", "text": text, "memory": memory}

        if state == "ACTION":

            text = gpt_reply(
                history,
                "Alright. Stay steady. We can build gently from here."
            )

            return {"step": "continue", "text": text, "memory": memory}

        # SAME

        text = gpt_reply(
            history,
            """
Sometimes grounding works quietly.

What feels most present right now?
"""
        )

        return {"step": "bridge", "text": text, "memory": memory}

    # -------------------------------------------------
    # BRIDGE (MOVE TOWARD ACTION)
    # -------------------------------------------------

    if step == "bridge":

        context = build_context(history, user_text)
        blocker = detect_blocker(context)
        spiral = detect_spiral(context)

        micro = generate_micro_action(blocker, spiral)

        text = gpt_reply(
            history,
            f"""
Let’s keep it small.

Try this:
{micro}
"""
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # CONTINUE
    # -------------------------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Stay grounded and move gently toward doable action.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "You’re here. Let’s take one steady breath and continue gently.",
        "memory": memory
    }