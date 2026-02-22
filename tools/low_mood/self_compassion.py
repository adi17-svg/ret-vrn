"""
Low Mood Tool: Self Compassion
Context-Aware + Last 6 Message Window
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6  # 👈 IMPORTANT

# =====================================================
# SYSTEM PROMPT
# =====================================================

BASE_PROMPT = """
You are a calm, warm self-compassion guide.

Rules:
- Warm and human tone
- No advice
- No fixing
- No problem solving
- Keep responses short (3–5 lines max)
- Validate first
- Encourage gentle self-talk
"""

# =====================================================
# GPT CALL (Only Last 6 Messages)
# =====================================================

def gpt_reply(history, instruction):

    messages = [
        {"role": "system", "content": BASE_PROMPT},
    ]

    # 👇 Only take last 6 messages
    if history:
        recent_history = history[-HISTORY_LIMIT:]
        messages.extend(recent_history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# STATE MACHINE
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []
    user_text = (user_text or "").strip()

    if not step:
        step = "await_activation"

    # -------------------------------------------------
    # ACTIVATION
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
    # USER SHARES EMOTION
    # -------------------------------------------------

    if step == "await_emotion":

        instruction = f"""
User said: "{user_text}"

Reflect warmly.
Use the recent conversation context if relevant.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "invite_self_talk",
            "text": text
        }

    # -------------------------------------------------
    # INVITE SELF TALK
    # -------------------------------------------------

    if step == "invite_self_talk":

        instruction = """
Ask gently:
"If a close friend felt this way, what would you tell them?"
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "reinforce",
            "text": text
        }

    # -------------------------------------------------
    # REINFORCE
    # -------------------------------------------------

    if step == "reinforce":

        instruction = f"""
User said: "{user_text}"

Reflect their compassionate words.
Then ask gently:
"Would you like to stay with this softness for a moment?"
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "continuation",
            "text": text
        }

    # -------------------------------------------------
    # CONTINUATION
    # -------------------------------------------------

    if step == "continuation":

        normalized = user_text.lower()

        if any(word in normalized for word in ["yes", "yeah", "okay", "sure"]):

            instruction = """
Guide one slow breath.
Encourage that gentle tone to settle.
Close softly.
"""

            text = gpt_reply(history, instruction)

            return {
                "step": "exit",
                "text": text
            }

        instruction = """
Acknowledge gently.
Appreciate their effort.
Close warmly.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "exit",
            "text": text
        }

    return {
        "step": "exit",
        "text": "We can pause here."
    }