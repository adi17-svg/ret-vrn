"""
Low Mood Tool: Getting Going With Action (RETVRN – Procedural Version)

Flow:
1. Detect struggle
2. Spiral detect (background)
3. Validate
4. Ask blocker
5. Reflect blocker + Ask permission
6. Suggest tiny step (spiral-based)
7. Close

Design principles:
- Topic agnostic
- Banner aligned: "Start small. No pressure."
- No direct solutions
- Permission before action
- No looping
"""

from spiral_dynamics import client


# ======================================
# SYSTEM PROMPT
# ======================================

SYSTEM_PROMPT = """
You are a calm, supportive mental health coach.

Rules:
- Keep responses short (2–4 lines)
- Sound natural and human
- Do not assume topics beyond what the user said
- Move gradually toward action
- Never rush into advice
- Always reinforce small steps
- Stay aligned with: "Start small. No pressure."
"""


# ======================================
# GPT HELPER
# ======================================

def gpt_reply(user_text: str | None, instruction: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text or ""},
        {"role": "assistant", "content": instruction}
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.3,
    )

    return resp.choices[0].message.content.strip()


# ======================================
# STRUGGLE DETECTION
# ======================================

def looks_like_struggle(text: str | None) -> bool:
    if not text:
        return False

    keywords = [
        "hard", "can't", "cannot", "difficult",
        "stuck", "lazy", "tired", "avoid",
        "procrastinate", "low", "no energy",
        "heavy", "overwhelmed"
    ]

    return any(k in text.lower() for k in keywords)


# ======================================
# SPIRAL DETECTION (BACKGROUND ONLY)
# ======================================

def detect_spiral_stage(text: str | None) -> str:
    if not text:
        return "Neutral"

    prompt = f"""
Classify emotional tone into one:

Blue – guilt, responsibility, structure focus
Red – resistance, impulse, frustration
Orange – productivity pressure, achievement stress
Green – emotional overwhelm, meaning focus
Neutral – unclear

Message: {text}

Return only one word.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# ======================================
# SPIRAL-BASED MICRO ACTION
# ======================================

def get_micro_action(stage: str) -> str:

    if stage == "Blue":
        return "Set a 2-minute timer and simply sit with the task in front of you."

    if stage == "Red":
        return "Give yourself a 60-second challenge — just begin, no thinking."

    if stage == "Orange":
        return "Complete one very small measurable piece — just the first step."

    if stage == "Green":
        return "Take one slow breath and gently start the smallest possible part."

    return "Begin with the smallest possible action — nothing more."


# ======================================
# MAIN HANDLER
# ======================================

def handle(step: str | None, user_text: str | None, memory: dict | None = None):

    memory = memory or {}

    # ----------------------------------
    # STEP 0 — INTRO (Banner safe)
    # ----------------------------------
    if step is None or step == "start":

        text = gpt_reply(
            user_text,
            """
Normalize low energy.
Reinforce we’ll take just one small step.
Ask what feels hardest to begin right now.
"""
        )

        return {"step": "ack", "text": text, "memory": memory}


    # ----------------------------------
    # STEP 1 — DETECT STRUGGLE
    # ----------------------------------
    if step == "ack":

        if not looks_like_struggle(user_text):
            text = gpt_reply(
                user_text,
                """
Respond warmly.
Invite them gently to share something that feels hard to start.
Keep it light.
"""
            )
            return {"step": "ack", "text": text, "memory": memory}

        stage = detect_spiral_stage(user_text)
        memory["spiral_stage"] = stage
        memory["struggle"] = user_text

        text = gpt_reply(
            user_text,
            """
Reflect what they shared briefly.
Reinforce we don’t have to solve it all.
Ask:
When you think about starting,
is it more low energy, distraction, or pressure?
"""
        )

        return {"step": "blocker", "text": text, "memory": memory}


    # ----------------------------------
    # STEP 2 — BLOCKER EXPLORE
    # ----------------------------------
    if step == "blocker":

        memory["blocker"] = user_text

        text = gpt_reply(
            user_text,
            """
Acknowledge the blocker gently.
Do NOT give advice yet.
Ask if they'd like to try a very small experiment.
One short permission question only.
"""
        )

        return {"step": "permission", "text": text, "memory": memory}


    # ----------------------------------
    # STEP 3 — PERMISSION GATE
    # ----------------------------------
    if step == "permission":

        if user_text and user_text.lower().strip() in [
            "yes", "yeah", "yep", "ok", "okay",
            "sure", "let's try", "i will try"
        ]:

            stage = memory.get("spiral_stage", "Neutral")
            micro_action = get_micro_action(stage)

            text = gpt_reply(
                user_text,
                f"""
Acknowledge their willingness.
Offer this tiny step:

{micro_action}

No extra explanation.
No additional questions.
"""
            )

            return {"step": "close", "text": text, "memory": memory}

        else:
            text = gpt_reply(
                user_text,
                """
Respect hesitation.
Reassure there's no pressure.
Close gently.
"""
            )

            return {"step": "close", "text": text, "memory": memory}


    # ----------------------------------
    # STEP 4 — CLOSE
    # ----------------------------------
    if step == "close":

        text = gpt_reply(
            user_text,
            """
Close warmly.
Reinforce that even considering change counts.
End clearly.
"""
        )

        return {"step": "exit", "text": text, "memory": memory}


    # ----------------------------------
    # SAFETY FALLBACK
    # ----------------------------------
    return {
        "step": "exit",
        "text": "We can pause here. You're in control.",
        "memory": memory
    }