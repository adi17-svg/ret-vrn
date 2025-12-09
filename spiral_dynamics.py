
# import os
# import json
# from openai import OpenAI
# # from config import A4F_API_KEY

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


# # ✅ Safely read key from Render environment
# # A4F_API_KEY = os.getenv("A4F_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# if not OPENAI_API_KEY:
#     raise ValueError("❌ Missing OPENAI_API_KEY environment variable")

# # if not A4F_API_KEY:
# #     raise ValueError("❌ Missing A4F_API_KEY environment variable — check Render settings.")
# # Initialize OpenAI client
# # client = OpenAI(api_key=A4F_API_KEY, base_url="https://api.a4f.co/v1")
# client = OpenAI(api_key=OPENAI_API_KEY)

# def detect_intent(entry: str) -> str:
#     prompt = (
#         "You are a Spiral Dynamics gatekeeper.\n"
#         "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
#         "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
#         f"Entry: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0,   
#     )
#     content = response.choices[0].message.content.lower()
#     return "spiral" if "spiral" in content else "chat"

# def classify_stage(entry: str) -> dict:
#     prompt = (
#         f"Analyze this user input and classify its dominant Spiral Dynamics stage from: {', '.join(STAGES)}.\n"
#         "Respond with JSON containing:\n"
#         "- 'primary_stage': The most dominant stage\n"
#         "- 'secondary_stage': Second most present stage (if any)\n"
#         "- 'confidence': Your confidence in primary stage (0-1)\n"
#         "- 'reason': Brief explanation of your choice\n\n"
#         f"Input: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.3,
#         response_format={"type": "json_object"}
#     )
#     try:
#         result = json.loads(response.choices[0].message.content)
#         return {
#             "stage": result.get("primary_stage", "Unknown"),
#             "secondary": result.get("secondary_stage"),
#             "confidence": float(result.get("confidence", 0)),
#             "reason": result.get("reason", "")
#         }
#     except Exception:
#         fallback = client.chat.completions.create(
#             model="gpt-4.1",
#             messages=[{"role": "user", "content": f"Classify this into one stage from {', '.join(STAGES)}: {entry}"}],
#             temperature=0
#         )
#         return {
#             "stage": fallback.choices[0].message.content.strip(),
#             "secondary": None,
#             "confidence": 1.0,
#             "reason": ""
#         }

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

# def generate_reflective_question(entry: str, reply_to: str = None) -> str:
#     context = f"\nReplying to: \"{reply_to}\"" if reply_to else ""
#     prompt = (
#         f"You are a Spiral Dynamics mentor. Based on the user's thoughts{context}, "
#         "ask one deep, emotionally resonant question (max 15 words). Just ask the question.\n\n"
#         f"User message: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.85
#     )
#     return response.choices[0].message.content.strip()

# def generate_gamified_prompt(stage: str, entry: str, evolution: bool = False) -> dict:
#     stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
#     prompt_template = (
#         f"Create a gamified interaction for a user at the {stage} stage of Spiral Dynamics. "
#         f"The user just shared: '{entry}'\n\n"
#         "Provide:\n"
#         "1. A VERY short reflective question (5-10 words) to deepen their awareness\n"
#         "2. A concrete action prompt (max 15 words) aligned with their stage\n"
#         "3. A stage-appropriate reward description\n"
#         "Format as JSON with keys: question, prompt, reward"
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt_template}],
#         temperature=0.7,
#         response_format={"type": "json_object"}
#     )
#     try:
#         content = json.loads(response.choices[0].message.content)
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {content.get('question','')}",
#             "gamified_prompt": f"💡 {content.get('prompt','')}",
#             "reward": content.get('reward') if evolution else stage_meta["reward"]
#         }
#     except Exception:
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What about this resonates most with you?",
#             "gamified_prompt": "💡 Reflect on how this shows up in your daily life",
#             "reward": stage_meta["reward"]
#         }
# spiral_dynamics.py

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

# def detect_intent(entry: str) -> str:
#     prompt = (
#         "You are a Spiral Dynamics gatekeeper.\n"
#         "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
#         "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
#         f"Entry: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0,
#     )
#     content = response.choices[0].message.content.lower()
#     return "spiral" if "spiral" in content else "chat"


# def classify_stage(entry: str, context: str = None) -> dict:
#     """
#     Classify the entry into a Spiral Dynamics stage.
#     Optional 'context' can be provided (short conversation history) to improve classification.
#     Returns dict with keys: stage, secondary, confidence, reason
#     """
#     ctx_part = f"\nContext:\n{context}\n" if context else ""
#     prompt = (
#         f"Analyze this user input and classify its dominant Spiral Dynamics stage from: {', '.join(STAGES)}.\n"
#         "Respond with JSON containing:\n"
#         "- 'primary_stage': The most dominant stage\n"
#         "- 'secondary_stage': Second most present stage (if any)\n"
#         "- 'confidence': Your confidence in primary stage (0-1)\n"
#         "- 'reason': Brief explanation of your choice\n\n"
#         f"{ctx_part}\nInput: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.3,
#         response_format={"type": "json_object"}
#     )
#     try:
#         result = json.loads(response.choices[0].message.content)
#         return {
#             "stage": result.get("primary_stage", "Unknown"),
#             "secondary": result.get("secondary_stage"),
#             "confidence": float(result.get("confidence", 0)),
#             "reason": result.get("reason", "")
#         }
#     except Exception:
#         # fallback: simple classification without structured JSON
#         fallback = client.chat.completions.create(
#             model="gpt-4.1",
#             messages=[{"role": "user", "content": f"Classify this into one stage from {', '.join(STAGES)}: {entry}"}],
#             temperature=0
#         )
#         return {
#             "stage": fallback.choices[0].message.content.strip(),
#             "secondary": None,
#             "confidence": 1.0,
#             "reason": ""
#         }


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


# def generate_reflective_question(entry: str, reply_to: str = None, context: str = None) -> str:
#     """
#     Generate a short reflective question based on the user's entry.
#     Accepts optional reply_to and a short context (conversation history) to make questions more targeted.
#     """
#     ctx = ""
#     if reply_to:
#         ctx += f"\nReplying to: \"{reply_to}\""
#     if context:
#         ctx += f"\nContext: {context}"
#     prompt = (
#         f"You are a Spiral Dynamics mentor. Based on the user's thoughts{ctx}, "
#         "ask one deep, emotionally resonant question (max 15 words). Just ask the question.\n\n"
#         f"User message: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.85
#     )
#     return response.choices[0].message.content.strip()


# def generate_gamified_prompt(stage: str, entry: str, evolution: bool = False) -> dict:
#     stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
#     prompt_template = (
#         f"Create a gamified interaction for a user at the {stage} stage of Spiral Dynamics. "
#         f"The user just shared: '{entry}'\n\n"
#         "Provide:\n"
#         "1. A VERY short reflective question (5-10 words) to deepen their awareness\n"
#         "2. A concrete action prompt (max 15 words) aligned with their stage\n"
#         "3. A stage-appropriate reward description\n"
#         "Format as JSON with keys: question, prompt, reward"
#     )
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[{"role": "user", "content": prompt_template}],
#         temperature=0.7,
#         response_format={"type": "json_object"}
#     )
#     try:
#         content = json.loads(response.choices[0].message.content)
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {content.get('question','')}",
#             "gamified_prompt": f"💡 {content.get('prompt','')}",
#             "reward": content.get('reward') if evolution else stage_meta["reward"]
#         }
#     except Exception:
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What about this resonates most with you?",
#             "gamified_prompt": "💡 Reflect on how this shows up in your daily life",
#             "reward": stage_meta["reward"]
#         }

# most useful
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
# # ----------------------------
# def detect_intent(entry: str) -> str:
#     """
#     Return 'spiral' if message is reflective/emotional/values-driven; otherwise 'chat'.
#     Deterministic (temperature=0) and expects exact word.
#     """
#     prompt = (
#         "You are a strict intent classifier. If the message expresses emotions, life struggle, "
#         "deep reflection, longing for change, or values-based thought, reply exactly with the single word: spiral\n"
#         "Otherwise reply exactly with the single word: chat\n\n"
#         f"Message: \"{entry}\""
#     )
#     try:
#         resp = client.chat.completions.create(
#             model="gpt-4.1",
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
#       - mind_mirror (short reflective sentence or None)   <-- NEW
#       - mood (single word mood label or None)             <-- NEW

#     Backwards-compatible: callers expecting 'stage','secondary','confidence','reason' still work.
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
#             model="gpt-4.1",
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
# # Evolution check (unchanged semantics)
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
# # Reflective question generator (keeps creative temp)
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
#             model="gpt-4.1",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.85,
#             max_tokens=60,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print("generate_reflective_question failed:", e)
#         return "What would that change look like for you?"


# # ----------------------------
# # Gamified prompt generator (robust JSON parsing, no response_format param)
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
#             model="gpt-4.1",
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
import os
import json
import re
from openai import OpenAI

# Constants and config
STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

STAGE_GAMIFIED_META = {
    "Beige": {"emoji": "🟤", "name": "Beige", "reward": "Basic awareness"},
    "Purple": {"emoji": "🟣", "name": "Purple", "reward": "Group belonging"},
    "Red": {"emoji": "🔴", "name": "Red", "reward": "Power attainment"},
    "Blue": {"emoji": "🔵", "name": "Blue", "reward": "Order and stability"},
    "Orange": {"emoji": "🟠", "name": "Orange", "reward": "Achievement"},
    "Green": {"emoji": "🟢", "name": "Green", "reward": "Community and connection"},
    "Yellow": {"emoji": "🟡", "name": "Yellow", "reward": "Integration"},
    "Turquoise": {"emoji": "🔷", "name": "Turquoise", "reward": "Global consciousness"},
}

# Read OpenAI key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=OPENAI_API_KEY)


# ----------------------------
# Intent detection (deterministic)

def detect_intent(entry: str) -> str:
    """
    Return:
      - 'ask_stage' if the message is the user asking about THEIR OWN Spiral Dynamics level
      - 'spiral'    if message is reflective/emotional/values-driven
      - 'chat'      otherwise (normal conversation)

    For existing users who already have a stage:
    - The endpoints decide what to do.
    - This function ONLY classifies the message itself.
    """
    if not entry or not entry.strip():
        return "chat"

    text = entry.strip()
    lower = f" {text.lower()} "  # padding for simple word-boundary checks

    # -------------------------
    # 1️⃣ Fast heuristic: user asking "what is MY stage/level/colour?"
    # -------------------------
    stage_keywords = [
        "spiral dynamics", "spiral dynamic", "spiral level", "spiral stage",
        "which stage am i", "what is my stage", "what's my stage",
        "what is my level", "what's my level",
        "which colour am i", "which color am i",
        "which spiral colour", "which spiral color",
        "what colour am i", "what color am i",
        "what stage am i in", "which stage in spiral",
        "my spiral stage", "my spiral level",
        "which stage do i belong", "which stage do i fit",
        "where do i fit in spiral", "where do i fall in spiral",
    ]

    # User is clearly talking about Spiral Dynamics + themselves
    if any(kw in lower for kw in stage_keywords):
        if any(p in lower for p in [" my ", " me ", " i ", " i'm ", " im ", " am i "]):
            return "ask_stage"

    # Very short messages like "my level?" / "which stage?"
    short = len(text.split()) <= 6
    short_markers = ["my level", "my stage", "which stage", "which level"]
    if short and any(kw in lower for kw in short_markers):
        return "ask_stage"

    # -------------------------
    # 2️⃣ Original LLM-based spiral vs chat classification
    # -------------------------
    prompt = (
        "You are a strict intent classifier. If the message expresses emotions, life struggle, "
        "deep reflection, longing for change, or values-based thought, reply exactly with the single word: spiral\n"
        "Otherwise reply exactly with the single word: chat\n\n"
        f"Message: \"{entry}\""
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=8,
        )
        content = resp.choices[0].message.content.strip().lower()
        return "spiral" if content.startswith("spiral") else "chat"
    except Exception as e:
        # on failure, default to chat to avoid over-triggering spiral logic
        print("detect_intent failed:", e)
        return "chat"


# ----------------------------
# def detect_intent(entry: str) -> str:
#     """
#     Return 'spiral' if message is reflective/emotional/values-driven; otherwise 'chat'.
#     Deterministic (temperature=0) and expects exact word.
#     """
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


# ----------------------------
# Stage classifier (robust, returns mind_mirror + mood)
# ----------------------------
def classify_stage(entry: str, context: str = None) -> dict:
    """
    Return:
      - stage (primary stage name string)
      - secondary (secondary stage or None)
      - confidence (float 0.0-1.0)
      - reason (short string)
      - mind_mirror (short reflective sentence or None)
      - mood (single word mood label or None)
    """
    ctx_part = f"\nContext:\n{context}\n" if context else ""
    prompt = (
        f"Analyze the following user text using Spiral Dynamics stages: {', '.join(STAGES)}.\n\n"
        "Return a JSON object with keys exactly: primary_stage, secondary_stage, confidence (0-1), reason, "
        "mind_mirror (one reflective sentence, max 20 words), mood (single word like bored/sad/anxious/hopeful).\n\n"
        f"{ctx_part}\nInput: \"{entry}\""
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=350,
        )
        raw = resp.choices[0].message.content.strip()
    except Exception as e:
        print("classify_stage AI call failed:", e)
        return {
            "stage": "Unknown",
            "secondary": None,
            "confidence": 0.0,
            "reason": "classification_failed",
            "mind_mirror": None,
            "mood": None,
        }

    # Try to parse JSON robustly
    parsed = None
    try:
        parsed = json.loads(raw)
    except Exception:
        m = re.search(r'(\{[\s\S]*\})', raw)
        if m:
            try:
                parsed = json.loads(m.group(1))
            except Exception:
                parsed = None

    # Fallback to simple line-parsing
    if not parsed:
        parsed = {}
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                parsed[k.strip().lower()] = v.strip()

    def _get(d, *keys):
        for k in keys:
            if k in d and d[k] not in (None, ""):
                return d[k]
        return None

    primary = _get(parsed, "primary_stage", "primary", "stage")
    secondary = _get(parsed, "secondary_stage", "secondary")
    reason = _get(parsed, "reason", "explanation")
    mind_mirror = _get(parsed, "mind_mirror", "mindmirror", "mirror", "reflection")
    mood = _get(parsed, "mood", "emotion", "feeling")

    # Normalize confidence
    confidence = 0.0
    raw_conf = _get(parsed, "confidence", "conf")
    if raw_conf is not None:
        try:
            confidence = float(str(raw_conf).strip())
            if confidence > 1:
                confidence = confidence / 100.0
        except Exception:
            confidence = 0.0

    if not primary:
        primary = "Unknown"

    return {
        "stage": primary,
        "secondary": secondary,
        "confidence": confidence,
        "reason": reason,
        "mind_mirror": mind_mirror,
        "mood": mood,
    }


# ----------------------------
# Evolution check
# ----------------------------
def check_evolution(last_stage: str, current_result: dict) -> str:
    if not last_stage:
        return None
    current_stage = current_result.get("stage", "Unknown")
    try:
        last_idx = STAGES.index(last_stage)
        current_idx = STAGES.index(current_stage)
        confidence = current_result.get("confidence", 0)
        if current_idx > last_idx and confidence >= 0.6:
            return f"🌱 Level Up! You're showing strong {current_stage} tendencies!"
        elif current_idx > last_idx:
            return f"🌀 Exploring {current_stage}, with elements of {last_stage}."
    except ValueError:
        pass
    return None


# ----------------------------
# Reflective question generator
# ----------------------------
def generate_reflective_question(entry: str, reply_to: str = None, context: str = None) -> str:
    ctx = ""
    if reply_to:
        ctx += f"\nReplying to: \"{reply_to}\""
    if context:
        ctx += f"\nContext: {context}"
    prompt = (
        f"You are a Spiral Dynamics mentor. Based on the user's thoughts{ctx}, "
        "ask ONE deep, emotionally resonant question (max 15 words). Only output the question.\n\n"
        f"User message: \"{entry}\""
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=60,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("generate_reflective_question failed:", e)
        return "What would that change look like for you?"


# ----------------------------
# Gamified prompt generator
# ----------------------------
def generate_gamified_prompt(stage: str, entry: str, evolution: bool = False) -> dict:
    stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
    prompt_template = (
        f"Create a gamified interaction for a user at the {stage} stage of Spiral Dynamics. "
        f"The user just shared: '{entry}'\n\n"
        "Return a JSON object with keys: question, prompt, reward.\n"
        " - question: 5-10 word reflective question\n"
        " - prompt: concrete action (max 15 words)\n"
        " - reward: short reward description\n"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_template}],
            temperature=0.7,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content.strip()
        try:
            content = json.loads(raw)
        except Exception:
            m = re.search(r'(\{[\s\S]*\})', raw)
            content = json.loads(m.group(1)) if m else {}
        return {
            "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {content.get('question','')}",
            "gamified_prompt": f"💡 {content.get('prompt','')}",
            "reward": content.get('reward') if evolution else stage_meta["reward"]
        }
    except Exception as e:
        print("generate_gamified_prompt failed:", e)
        return {
            "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What about this resonates most with you?",
            "gamified_prompt": "💡 Reflect on how this shows up in your daily life",
            "reward": stage_meta["reward"]
        }