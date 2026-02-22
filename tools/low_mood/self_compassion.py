"""
Low Mood Tool: Self Compassion
Context-Aware + Step Based + Production Safe
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# SYSTEM PROMPT
# =====================================================

BASE_PROMPT = """
You are a calm, warm self-compassion guide inside a mental wellness app.

Rules:
- Warm and human tone
- No advice
- No fixing
- No problem solving
- Keep responses short (3–5 lines max)
- Validate first
- Encourage gentle self-talk
- Use previous user context naturally if helpful
"""

# =====================================================
# GPT CALL (History Aware)
# =====================================================

def gpt_reply(history, instruction):

    messages = [
        {"role": "system", "content": BASE_PROMPT},
    ]

    # include previous tool conversation
    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN TOOL STATE MACHINE
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []
    user_text = (user_text or "").strip()

    if not step:
        step = "await_activation"

    # -------------------------------------------------
    # 1️⃣ ACTIVATION
    # -------------------------------------------------

    if step == "await_activation":

        if user_text.upper() != "READY":
            return {
                "step": "await_activation",
                "text": "This is a short self-compassion space.\nType READY when you want to begin."
            }

        return {
            "step": "await_emotion",
            "text": "What feels heavy right now?"
        }

    # -------------------------------------------------
    # 2️⃣ USER SHARES EMOTION
    # -------------------------------------------------

    if step == "await_emotion":

        instruction = f"""
User just shared: "{user_text}"

Reflect their experience warmly.
Acknowledge the emotional weight.
Use earlier context if relevant.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "invite_self_talk",
            "text": text
        }

    # -------------------------------------------------
    # 3️⃣ INVITE SELF TALK
    # -------------------------------------------------

    if step == "invite_self_talk":

        instruction = """
Gently ask:
"If a close friend felt this way, what would you tell them?"

Keep tone soft and natural.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "reinforce",
            "text": text
        }

    # -------------------------------------------------
    # 4️⃣ REINFORCE USER'S COMPASSION
    # -------------------------------------------------

    if step == "reinforce":

        instruction = f"""
User responded with self-talk: "{user_text}"

Reflect their compassionate words.
Help them internalize that kindness.
Then gently ask:
"Would you like to stay with this softness for a moment?"
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "continuation",
            "text": text
        }

    # -------------------------------------------------
    # 5️⃣ CONTINUATION
    # -------------------------------------------------

    if step == "continuation":

        normalized = user_text.lower()

        if any(word in normalized for word in ["yes", "yeah", "okay", "sure"]):

            instruction = """
Guide one slow breath.
Encourage them to let that kind tone settle inside.
Close gently.
"""

            text = gpt_reply(history, instruction)

            return {
                "step": "exit",
                "text": text
            }

        instruction = """
Acknowledge gently.
Reassure them that even trying this matters.
Close warmly.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "exit",
            "text": text
        }

    # -------------------------------------------------
    # 6️⃣ EXIT
    # -------------------------------------------------

    return {
        "step": "exit",
        "text": "We can pause here."
    }