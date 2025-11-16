
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

import os
import json
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

def detect_intent(entry: str) -> str:
    prompt = (
        "You are a Spiral Dynamics gatekeeper.\n"
        "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
        "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
        f"Entry: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    content = response.choices[0].message.content.lower()
    return "spiral" if "spiral" in content else "chat"


def classify_stage(entry: str, context: str = None) -> dict:
    """
    Classify the entry into a Spiral Dynamics stage.
    Optional 'context' can be provided (short conversation history) to improve classification.
    Returns dict with keys: stage, secondary, confidence, reason
    """
    ctx_part = f"\nContext:\n{context}\n" if context else ""
    prompt = (
        f"Analyze this user input and classify its dominant Spiral Dynamics stage from: {', '.join(STAGES)}.\n"
        "Respond with JSON containing:\n"
        "- 'primary_stage': The most dominant stage\n"
        "- 'secondary_stage': Second most present stage (if any)\n"
        "- 'confidence': Your confidence in primary stage (0-1)\n"
        "- 'reason': Brief explanation of your choice\n\n"
        f"{ctx_part}\nInput: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    try:
        result = json.loads(response.choices[0].message.content)
        return {
            "stage": result.get("primary_stage", "Unknown"),
            "secondary": result.get("secondary_stage"),
            "confidence": float(result.get("confidence", 0)),
            "reason": result.get("reason", "")
        }
    except Exception:
        # fallback: simple classification without structured JSON
        fallback = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": f"Classify this into one stage from {', '.join(STAGES)}: {entry}"}],
            temperature=0
        )
        return {
            "stage": fallback.choices[0].message.content.strip(),
            "secondary": None,
            "confidence": 1.0,
            "reason": ""
        }


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


def generate_reflective_question(entry: str, reply_to: str = None, context: str = None) -> str:
    """
    Generate a short reflective question based on the user's entry.
    Accepts optional reply_to and a short context (conversation history) to make questions more targeted.
    """
    ctx = ""
    if reply_to:
        ctx += f"\nReplying to: \"{reply_to}\""
    if context:
        ctx += f"\nContext: {context}"
    prompt = (
        f"You are a Spiral Dynamics mentor. Based on the user's thoughts{ctx}, "
        "ask one deep, emotionally resonant question (max 15 words). Just ask the question.\n\n"
        f"User message: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85
    )
    return response.choices[0].message.content.strip()


def generate_gamified_prompt(stage: str, entry: str, evolution: bool = False) -> dict:
    stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
    prompt_template = (
        f"Create a gamified interaction for a user at the {stage} stage of Spiral Dynamics. "
        f"The user just shared: '{entry}'\n\n"
        "Provide:\n"
        "1. A VERY short reflective question (5-10 words) to deepen their awareness\n"
        "2. A concrete action prompt (max 15 words) aligned with their stage\n"
        "3. A stage-appropriate reward description\n"
        "Format as JSON with keys: question, prompt, reward"
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt_template}],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    try:
        content = json.loads(response.choices[0].message.content)
        return {
            "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {content.get('question','')}",
            "gamified_prompt": f"💡 {content.get('prompt','')}",
            "reward": content.get('reward') if evolution else stage_meta["reward"]
        }
    except Exception:
        return {
            "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What about this resonates most with you?",
            "gamified_prompt": "💡 Reflect on how this shows up in your daily life",
            "reward": stage_meta["reward"]
        }
