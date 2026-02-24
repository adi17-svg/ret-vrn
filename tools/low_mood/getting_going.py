"""
Low Mood Tool: Getting Going With Action
Adaptive Context-Aware Version (RETVRN v3)

Upgrades:
- Context-based detection (history aware)
- Previous step aware progress detection
- Confusion / distress branching
- Adaptive flow engine
"""

from openai import OpenAI

client = OpenAI()
HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are a calm, grounded mental health coach.

Rules:
- Keep responses short (2–4 lines max)
- Be natural and human
- No repetitive praise
- Subtle validation only
- No lecturing
- Keep tone grounded
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
        temperature=0.5,
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# CONTEXT BUILDER
# =====================================================

def build_context(history, user_text):
    recent = " ".join([msg.get("text", "") for msg in history[-3:]])
    return f"{recent} {user_text}".strip()


# =====================================================
# STATE SIGNAL DETECTION
# =====================================================

def detect_state_signal(context, last_step=None):

    prompt = f"""
Analyze the emotional state in this conversation:

Context:
"{context}"

If last step exists:
"{last_step}"

Classify into ONE:

PROGRESS – user attempted/completed step
CONFUSION – unclear reaction (e.g., weird, unsure)
DISTRESS – emotional spike or overwhelm
RESISTANCE – avoidance or pushback
NEUTRAL – none of above

Return one word only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# BLOCKER DETECTION (Context Aware)
# =====================================================

def extract_blocker_type(context):

    prompt = f"""
Classify the main blocker in this context:

Options:
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
# STEP GENERATOR
# =====================================================

def generate_step(task, blocker, expand=False):

    size_instruction = (
        "Generate one slightly bigger but manageable next step (5–10 minutes max)."
        if expand
        else "Generate one extremely small first step."
    )

    prompt = f"""
Task: "{task}"
Blocker: {blocker}

{size_instruction}
No explanation.
One action only.
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

    if not user_text:
        return {
            "step": "continue",
            "text": "What feels hard to start right now?",
            "memory": memory
        }

    # ----------------------------------
    # Build context
    # ----------------------------------

    context = build_context(history, user_text)
    last_step = memory.get("last_step")

    state = detect_state_signal(context, last_step)

    # ----------------------------------
    # PROGRESS BRANCH
    # ----------------------------------

    if state == "PROGRESS" and memory.get("task"):

        next_step = generate_step(
            task=memory.get("task"),
            blocker=memory.get("blocker", "UNCLEAR"),
            expand=True
        )

        memory["last_step"] = next_step

        response = gpt_reply(
            history,
            f"""
Brief subtle validation.

Then suggest:
{next_step}
"""
        )

        return {
            "step": "continue",
            "text": response,
            "memory": memory
        }

    # ----------------------------------
    # CONFUSION BRANCH
    # ----------------------------------

    if state == "CONFUSION":

        response = gpt_reply(
            history,
            """
Acknowledge gently.

Ask what felt strange or uncomfortable about it.
Keep it short.
"""
        )

        return {
            "step": "continue",
            "text": response,
            "memory": memory
        }

    # ----------------------------------
    # DISTRESS BRANCH
    # ----------------------------------

    if state == "DISTRESS":

        response = gpt_reply(
            history,
            """
Validate the heaviness briefly.

Ask if they'd prefer an even smaller step or pause.
"""
        )

        return {
            "step": "continue",
            "text": response,
            "memory": memory
        }

    # ----------------------------------
    # RESISTANCE BRANCH
    # ----------------------------------

    if state == "RESISTANCE":

        response = gpt_reply(
            history,
            """
Acknowledge resistance without pushing.

Ask what feels hardest about doing it.
"""
        )

        return {
            "step": "continue",
            "text": response,
            "memory": memory
        }

    # ----------------------------------
    # DEFAULT / FRESH START
    # ----------------------------------

    blocker_type = extract_blocker_type(context)

    memory["blocker"] = blocker_type
    memory["task"] = user_text

    micro_step = generate_step(
        task=user_text,
        blocker=blocker_type,
        expand=False
    )

    memory["last_step"] = micro_step

    response = gpt_reply(
        history,
        f"""
Reflect briefly on what feels hard.

Then suggest:
{micro_step}
"""
    )

    return {
        "step": "continue",
        "text": response,
        "memory": memory
    }