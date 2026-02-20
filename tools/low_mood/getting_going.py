"""
Low Mood Tool: Getting Going With Action (RETVRN FINAL)

Flow:
1. Detect struggle
2. Spiral detect (background)
3. Validate (banner-aware)
4. Ask blocker (specific, not repetitive)
5. Suggest tiny step (spiral-based)
6. Close

Design:
- Topic agnostic
- Banner-consistent tone
- GPT only for tone
- Tool controls logic
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
- Do not repeat the user's sentence mechanically
- Do not assume topics beyond what the user said
- Reinforce small steps
- Never overanalyze
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
# MICRO ACTION GENERATOR (SPIRAL-BASED)
# ======================================

def get_micro_action(stage: str) -> str:

    if stage == "Blue":
        return "Set a timer for 2 minutes and just sit with it."

    if stage == "Red":
        return "Give yourself a 60-second challenge — just begin."

    if stage == "Orange":
        return "Do one tiny measurable step — just the first piece."

    if stage == "Green":
        return "Take one slow breath and gently start the smallest part."

    return "Just begin with the smallest possible action — nothing more."


# ======================================
# MAIN HANDLER
# ======================================

def handle(step: str | None, user_text: str | None, memory: dict | None = None):

    memory = memory or {}

    # ----------------------------------
    # STEP 0 — INTRO (BANNER SAFE)
    # ----------------------------------
    if step is None or step == "start":

        text = gpt_reply(
            user_text,
            """
Normalize low energy.
Align with banner: start small, no pressure.
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
Gently invite them to share something that feels hard to start.
Keep it light.
"""
            )
            return {"step": "ack", "text": text, "memory": memory}

        # Spiral background detection
        stage = detect_spiral_stage(user_text)
        memory["spiral_stage"] = stage
        memory["struggle"] = user_text

        text = gpt_reply(
            user_text,
            """
Briefly reflect what they shared.
Reinforce we’ll take just one small step.
Then ask:
When you think about starting, 
is it more low energy, distraction, or pressure?
"""
        )

        return {"step": "blocker", "text": text, "memory": memory}


    # ----------------------------------
    # STEP 2 — BLOCKER IDENTIFIED
    # ----------------------------------
    if step == "blocker":

        memory["blocker"] = user_text
        stage = memory.get("spiral_stage", "Neutral")

        micro_action = get_micro_action(stage)

        text = gpt_reply(
            user_text,
            f"""
Based on what they shared,
offer this tiny step:

{micro_action}

No deep explanation.
No multiple options.
Close naturally after offering.
"""
        )

        return {"step": "close", "text": text, "memory": memory}


    # ----------------------------------
    # STEP 3 — CLOSE
    # ----------------------------------
    if step == "close":

        text = gpt_reply(
            user_text,
            """
Close warmly.
Reinforce that even considering a small step counts.
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