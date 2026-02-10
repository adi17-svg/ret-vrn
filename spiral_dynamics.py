
# import os
# import json
# import re
# from openai import OpenAI

# # Constants and config
# STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

# STAGE_GAMIFIED_META = {
#     "Beige": {"emoji": "🟤", "name": "Beige", "reward": "Basic awareness"},
#     "Purple": {"emoji": "🟣", "name": "Purple", "reward": "Group belonging"},
#     "Red": {"emoji": "🔴", "name": "Red", "reward": "Power attainment"},
#     "Blue": {"emoji": "🔵", "name": "Blue", "reward": "Order and stability"},
#     "Orange": {"emoji": "🟠", "name": "Orange", "reward": "Achievement"},
#     "Green": {"emoji": "🟢", "name": "Green", "reward": "Community and connection"},
#     "Yellow": {"emoji": "🟡", "name": "Yellow", "reward": "Integration"},
#     "Turquoise": {"emoji": "🔷", "name": "Turquoise", "reward": "Global consciousness"},
# }

# # Read OpenAI key from environment
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise ValueError("❌ Missing OPENAI_API_KEY environment variable")

# client = OpenAI(api_key=OPENAI_API_KEY)


# # ----------------------------
# # Intent detection (deterministic)

# def detect_intent(entry: str) -> str:
#     """
#     Return:
#       - 'ask_stage' if the message is the user asking about THEIR OWN Spiral Dynamics level
#       - 'spiral'    if message is reflective/emotional/values-driven
#       - 'chat'      otherwise (normal conversation)

#     For existing users who already have a stage:
#     - The endpoints decide what to do.
#     - This function ONLY classifies the message itself.
#     """
#     if not entry or not entry.strip():
#         return "chat"

#     text = entry.strip()
#     lower = f" {text.lower()} "  # padding for simple word-boundary checks

#     # -------------------------
#     # 1️⃣ Fast heuristic: user asking "what is MY stage/level/colour?"
#     # -------------------------
#     stage_keywords = [
#         "spiral dynamics", "spiral dynamic", "spiral level", "spiral stage",
#         "which stage am i", "what is my stage", "what's my stage",
#         "what is my level", "what's my level",
#         "which colour am i", "which color am i",
#         "which spiral colour", "which spiral color",
#         "what colour am i", "what color am i",
#         "what stage am i in", "which stage in spiral",
#         "my spiral stage", "my spiral level",
#         "which stage do i belong", "which stage do i fit",
#         "where do i fit in spiral", "where do i fall in spiral",
#     ]

#     # User is clearly talking about Spiral Dynamics + themselves
#     if any(kw in lower for kw in stage_keywords):
#         if any(p in lower for p in [" my ", " me ", " i ", " i'm ", " im ", " am i "]):
#             return "ask_stage"

#     # Very short messages like "my level?" / "which stage?"
#     short = len(text.split()) <= 6
#     short_markers = ["my level", "my stage", "which stage", "which level"]
#     if short and any(kw in lower for kw in short_markers):
#         return "ask_stage"

#     # -------------------------
#     # 2️⃣ Original LLM-based spiral vs chat classification
#     # -------------------------
#     prompt = (
#         "You are a strict intent classifier. If the message expresses emotions, life struggle, "
#         "deep reflection, longing for change, or values-based thought, reply exactly with the single word: spiral\n"
#         "Otherwise reply exactly with the single word: chat\n\n"
#         f"Message: \"{entry}\""
#     )
#     try:
#         resp = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.0,
#             max_tokens=8,
#         )
#         content = resp.choices[0].message.content.strip().lower()
#         return "spiral" if content.startswith("spiral") else "chat"
#     except Exception as e:
#         # on failure, default to chat to avoid over-triggering spiral logic
#         print("detect_intent failed:", e)
#         return "chat"


# # ----------------------------
# # Stage classifier (robust, returns mind_mirror + mood)
# # ----------------------------
# def classify_stage(entry: str, context: str = None) -> dict:
#     """
#     Return:
#       - stage (primary stage name string)
#       - secondary (secondary stage or None)
#       - confidence (float 0.0-1.0)
#       - reason (short string)
#       - mind_mirror (short reflective sentence or None)
#       - mood (single word mood label or None)
#     """
#     ctx_part = f"\nContext:\n{context}\n" if context else ""
#     prompt = (
#         f"Analyze the following user text using Spiral Dynamics stages: {', '.join(STAGES)}.\n\n"
#         "Return a JSON object with keys exactly: primary_stage, secondary_stage, confidence (0-1), reason, "
#         "mind_mirror (one reflective sentence, max 20 words), mood (single word like bored/sad/anxious/hopeful).\n\n"
#         f"{ctx_part}\nInput: \"{entry}\""
#     )

#     try:
#         resp = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.0,
#             max_tokens=350,
#         )
#         raw = resp.choices[0].message.content.strip()
#     except Exception as e:
#         print("classify_stage AI call failed:", e)
#         return {
#             "stage": "Unknown",
#             "secondary": None,
#             "confidence": 0.0,
#             "reason": "classification_failed",
#             "mind_mirror": None,
#             "mood": None,
#         }

#     # Try to parse JSON robustly
#     parsed = None
#     try:
#         parsed = json.loads(raw)
#     except Exception:
#         m = re.search(r'(\{[\s\S]*\})', raw)
#         if m:
#             try:
#                 parsed = json.loads(m.group(1))
#             except Exception:
#                 parsed = None

#     # Fallback to simple line-parsing
#     if not parsed:
#         parsed = {}
#         for line in raw.splitlines():
#             if ":" in line:
#                 k, v = line.split(":", 1)
#                 parsed[k.strip().lower()] = v.strip()

#     def _get(d, *keys):
#         for k in keys:
#             if k in d and d[k] not in (None, ""):
#                 return d[k]
#         return None

#     primary = _get(parsed, "primary_stage", "primary", "stage")
#     secondary = _get(parsed, "secondary_stage", "secondary")
#     reason = _get(parsed, "reason", "explanation")
#     mind_mirror = _get(parsed, "mind_mirror", "mindmirror", "mirror", "reflection")
#     mood = _get(parsed, "mood", "emotion", "feeling")

#     # Normalize confidence
#     confidence = 0.0
#     raw_conf = _get(parsed, "confidence", "conf")
#     if raw_conf is not None:
#         try:
#             confidence = float(str(raw_conf).strip())
#             if confidence > 1:
#                 confidence = confidence / 100.0
#         except Exception:
#             confidence = 0.0

#     if not primary:
#         primary = "Unknown"

#     return {
#         "stage": primary,
#         "secondary": secondary,
#         "confidence": confidence,
#         "reason": reason,
#         "mind_mirror": mind_mirror,
#         "mood": mood,
#     }


# # ----------------------------
# # Evolution check
# # ----------------------------
# def check_evolution(last_stage: str, current_result: dict) -> str:
#     if not last_stage:
#         return None
#     current_stage = current_result.get("stage", "Unknown")
#     try:
#         last_idx = STAGES.index(last_stage)
#         current_idx = STAGES.index(current_stage)
#         confidence = current_result.get("confidence", 0)
#         if current_idx > last_idx and confidence >= 0.6:
#             return f"🌱 Level Up! You're showing strong {current_stage} tendencies!"
#         elif current_idx > last_idx:
#             return f"🌀 Exploring {current_stage}, with elements of {last_stage}."
#     except ValueError:
#         pass
#     return None


# # ----------------------------
# # Reflective question generator
# # ----------------------------
# def generate_reflective_question(entry: str, reply_to: str = None, context: str = None) -> str:
#     ctx = ""
#     if reply_to:
#         ctx += f"\nReplying to: \"{reply_to}\""
#     if context:
#         ctx += f"\nContext: {context}"
#     prompt = (
#         f"You are a Spiral Dynamics mentor. Based on the user's thoughts{ctx}, "
#         "ask ONE deep, emotionally resonant question (max 15 words). Only output the question.\n\n"
#         f"User message: \"{entry}\""
#     )
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.85,
#             max_tokens=60,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print("generate_reflective_question failed:", e)
#         return "What would that change look like for you?"


# # ----------------------------
# # Gamified prompt generator
# # ----------------------------
# def generate_gamified_prompt(stage: str, entry: str, evolution: bool = False) -> dict:
#     stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
#     prompt_template = (
#         f"Create a gamified interaction for a user at the {stage} stage of Spiral Dynamics. "
#         f"The user just shared: '{entry}'\n\n"
#         "Return a JSON object with keys: question, prompt, reward.\n"
#         " - question: 5-10 word reflective question\n"
#         " - prompt: concrete action (max 15 words)\n"
#         " - reward: short reward description\n"
#     )
#     try:
#         resp = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt_template}],
#             temperature=0.7,
#             max_tokens=200,
#         )
#         raw = resp.choices[0].message.content.strip()
#         try:
#             content = json.loads(raw)
#         except Exception:
#             m = re.search(r'(\{[\s\S]*\})', raw)
#             content = json.loads(m.group(1)) if m else {}
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {content.get('question','')}",
#             "gamified_prompt": f"💡 {content.get('prompt','')}",
#             "reward": content.get('reward') if evolution else stage_meta["reward"]
#         }
#     except Exception as e:
#         print("generate_gamified_prompt failed:", e)
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What about this resonates most with you?",
#             "gamified_prompt": "💡 Reflect on how this shows up in your daily life",
#             "reward": stage_meta["reward"]
#         }


# # ----------------------------
# # Mission feedback line (stage + mood + completion)
# # ----------------------------
# def build_mission_feedback_line(stage: str, mood: str, completion: str = "full") -> str:
#     """
#     Small, friendly line after a mission-related spiral reply.
#     Uses:
#       - stage: Spiral Dynamics stage (string)
#       - mood:  simple mood label from classifier (string or None)
#       - completion: 'full' / 'partial' / 'none' (currently we use 'full')
#     """
#     if not completion or completion == "none":
#         return ""

#     stage = (stage or "Unknown").strip()
#     mood_l = (mood or "").strip().lower()

#     # 1) Base line depending on completion
#     if completion == "partial":
#         line = "I’m really glad you at least touched this mission today. That effort still matters."
#     else:  # full
#         line = "I’m really glad you showed up for yourself with this mission today."

#     # 2) Mood-sensitive soft addition
#     heavy_moods = {"sad", "low", "tired", "anxious", "overwhelmed", "drained", "stressed"}
#     light_moods = {"calm", "relieved", "okay", "peaceful", "light"}
#     proud_moods = {"proud", "hopeful", "motivated", "excited", "inspired"}

#     extra = ""

#     if mood_l in heavy_moods:
#         extra = " It’s okay if it still feels a bit heavy — you’re allowed to go slowly."
#     elif mood_l in light_moods:
#         extra = " Notice how your system feels after doing this, even in small ways."
#     elif mood_l in proud_moods:
#         extra = " Let that small sense of progress sink in for a moment."

#     # 3) Stage-flavoured tiny hint (very soft, no pressure)
#     stage_l = stage.lower()
#     stage_hint = ""

#     if stage_l == "green":
#         stage_hint = " This kind of gentle action really fits your care-for-people side."
#     elif stage_l == "orange":
#         stage_hint = " These small experiments quietly support your longer-term goals."
#     elif stage_l == "blue":
#         stage_hint = " Keeping small promises like this slowly builds inner stability."
#     elif stage_l == "yellow":
#         stage_hint = " Noticing how this mission connects different parts of your life can be powerful."
#     elif stage_l == "purple":
#         stage_hint = " Any movement you make here also supports your sense of belonging and safety."
#     # Other stages → no extra hint, keep it simple

#     return (line + extra + stage_hint).strip()
import os
import json
import re
from openai import OpenAI

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

STAGE_GAMIFIED_META = {
    "Beige": {"emoji": "🟤", "reward": "Basic awareness"},
    "Purple": {"emoji": "🟣", "reward": "Group belonging"},
    "Red": {"emoji": "🔴", "reward": "Power attainment"},
    "Blue": {"emoji": "🔵", "reward": "Order and stability"},
    "Orange": {"emoji": "🟠", "reward": "Achievement"},
    "Green": {"emoji": "🟢", "reward": "Community and connection"},
    "Yellow": {"emoji": "🟡", "reward": "Integration"},
    "Turquoise": {"emoji": "🔷", "reward": "Global consciousness"},
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# ---------------------------------------------------
# 🧠 SINGLE BRAIN FUNCTION
# ---------------------------------------------------

def analyze_spiral_and_generate(
    entry: str,
    context: str | None = None,
    reply_to: str | None = None,
):
    """
    One GPT call:
    - Detect stage
    - Detect mood
    - Generate reflective question (if needed)
    - Generate mission (if appropriate)
    - Generate final reply
    """

    ctx_part = f"\nContext:\n{context}" if context else ""
    reply_part = f"\nReplying to: {reply_to}" if reply_to else ""

    system_prompt = f"""
You are a warm, emotionally intelligent Spiral Dynamics companion.

User message: "{entry}"
{ctx_part}
{reply_part}

Steps:
1. Detect Spiral stage from: {', '.join(STAGES)}
2. Detect mood (one word like sad/anxious/hopeful/confused/proud/etc.)
3. Decide response_type:
   - validate (if emotional pain)
   - reflect (if confused/stuck)
   - act (if stable + growth-oriented)
   - listen (normal chat)

4. Generate:
   - reply (short, warm, grounded)
   - mind_mirror (short reflective sentence OR null)
   - mission (short action OR null)

Return ONLY valid JSON:

{{
  "stage": "...",
  "confidence": 0-1,
  "mood": "...",
  "response_type": "...",
  "mind_mirror": "... or null",
  "mission": "... or null",
  "reply": "..."
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.7,
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()

    except Exception as e:
        print("GPT error:", e)
        return _fallback(entry)

    # ---------------------------------------------------
    # Robust JSON parsing
    # ---------------------------------------------------

    try:
        parsed = json.loads(raw)
    except Exception:
        match = re.search(r'(\{[\s\S]*\})', raw)
        if match:
            try:
                parsed = json.loads(match.group(1))
            except:
                return _fallback(entry)
        else:
            return _fallback(entry)

    return {
        "stage": parsed.get("stage"),
        "confidence": float(parsed.get("confidence", 0)),
        "mood": parsed.get("mood"),
        "response_type": parsed.get("response_type"),
        "mind_mirror": parsed.get("mind_mirror"),
        "mission": parsed.get("mission"),
        "reply": parsed.get("reply"),
    }


# ---------------------------------------------------
# Fallback Safety
# ---------------------------------------------------

def _fallback(entry: str):
    return {
        "stage": None,
        "confidence": 0.0,
        "mood": None,
        "response_type": "listen",
        "mind_mirror": None,
        "mission": None,
        "reply": "I'm here with you. Tell me a little more.",
    }


# ---------------------------------------------------
# Evolution Check (unchanged logic)
# ---------------------------------------------------

def check_evolution(last_stage: str, current_stage: str, confidence: float):
    if not last_stage or not current_stage:
        return None

    try:
        last_idx = STAGES.index(last_stage)
        current_idx = STAGES.index(current_stage)

        if current_idx > last_idx and confidence >= 0.6:
            return f"🌱 Level Up! You're showing stronger {current_stage} tendencies."
        elif current_idx > last_idx:
            return f"🌀 Exploring {current_stage}, still integrating {last_stage}."
    except ValueError:
        pass

    return None
