
import os
import json
from openai import OpenAI
from config import A4F_API_KEY

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

# Initialize OpenAI client
client = OpenAI(api_key=A4F_API_KEY, base_url="https://api.a4f.co/v1")

def detect_intent(entry: str) -> str:
    prompt = (
        "You are a Spiral Dynamics gatekeeper.\n"
        "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
        "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
        f"Entry: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="provider-3/gpt-4.1",
        # model="provider-3/gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    content = response.choices[0].message.content.lower()
    return "spiral" if "spiral" in content else "chat"

def classify_stage(entry: str) -> dict:
    prompt = (
        f"Analyze this user input and classify its dominant Spiral Dynamics stage from: {', '.join(STAGES)}.\n"
        "Respond with JSON containing:\n"
        "- 'primary_stage': The most dominant stage\n"
        "- 'secondary_stage': Second most present stage (if any)\n"
        "- 'confidence': Your confidence in primary stage (0-1)\n"
        "- 'reason': Brief explanation of your choice\n\n"
        f"Input: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="provider-3/gpt-4.1",
        # model="provider-5/gpt-5-nano",
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
        fallback = client.chat.completions.create(
            model="provider-3/gpt-4.1",
            # model="provider-5/gpt-5-nano",
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

def generate_reflective_question(entry: str, reply_to: str = None) -> str:
    context = f"\nReplying to: \"{reply_to}\"" if reply_to else ""
    prompt = (
        f"You are a Spiral Dynamics mentor. Based on the user's thoughts{context}, "
        "ask one deep, emotionally resonant question (max 15 words). Just ask the question.\n\n"
        f"User message: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="provider-3/gpt-4.1",
        # model="provider-5/gpt-5-nano",
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
        model="provider-3/gpt-4.1",
        # model="provider-5/gpt-5-nano",
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

# import os
# import json
# from openai import OpenAI
# from config import A4F_API_KEY

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

# # Initialize OpenAI client
# client = OpenAI(api_key=A4F_API_KEY, base_url="https://api.a4f.co/v1")

# def detect_intent(entry: str) -> str:
#     prompt = (
#         "You are a Spiral Dynamics gatekeeper.\n"
#         "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
#         "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
#         f"Entry: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         # model="provider-3/gpt-4.1",
#         model="provider-5/gpt-5-nano",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0,
#     )
#     content = response.choices[0].message.content.lower()
#     return "spiral" if "spiral" in content else "chat"


# def classify_stage(entry: str) -> dict:
#     prompt = (
#         f"Analyze this user input and classify its dominant Spiral Dynamics stage from: {', '.join(STAGES)}.\n"
#         "Respond ONLY with JSON containing:\n"
#         "- 'primary_stage': The most dominant stage name only (no explanation)\n"
#         "- 'secondary_stage': Second most present stage (if any)\n"
#         "- 'confidence': Confidence in primary stage (0-1)\n"
#         "- 'reason': Empty string ('')\n\n"
#         f"Input: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         # model="provider-3/gpt-4.1",
#         model="provider-5/gpt-5-nano",
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
#             "reason": ""  # no explanation for model 5
#         }
#     except Exception:
#         fallback = client.chat.completions.create(
#             model="provider-5/gpt-5-nano",
#             messages=[{"role": "user", "content": f"Return only one stage name from {', '.join(STAGES)}: {entry}"}],
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
#         "Generate ONLY one short reflective question (max 10 words). "
#         "Do NOT explain or add context — only output the question text.\n\n"
#         f"User message: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         # model="provider-3/gpt-4.1",
#         model="provider-5/gpt-5-nano",
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
#         "1. A VERY short reflective question (5-10 words) ONLY (no explanation)\n"
#         "2. A concrete action prompt (max 15 words)\n"
#         "3. A reward line aligned with the stage\n"
#         "Format as JSON with keys: question, prompt, reward"
#     )
#     response = client.chat.completions.create(
#         # model="provider-3/gpt-4.1",
#         model="provider-5/gpt-5-nano",
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
















# Useless code
# import json
# from openai import OpenAI
# from config import A4F_API_KEY

# STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

# client = OpenAI(api_key=A4F_API_KEY, base_url="https://api.a4f.co/v1")

# def detect_intent(entry: str) -> str:
#     """
#     Detect if the journal entry reflects Spiral Dynamics related depth ('spiral')
#     or just light chat ('chat').
#     """
#     prompt = (
#         "You are a Spiral Dynamics gatekeeper.\n"
#         "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
#         "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
#         f"Entry: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0,
#     )
#     content = response.choices[0].message.content.lower()
#     return "spiral" if "spiral" in content else "chat"

# def classify_stage(entry: str) -> dict:
#     """
#     Classifies the Spiral Dynamics stage of the journal entry.
#     Returns a dictionary with keys: 'stage', 'secondary', 'confidence', 'reason'.
#     """
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
#         model="provider-3/gpt-4",
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
#         # Fallback if JSON cannot be parsed
#         return {"stage": "Unknown", "secondary": None, "confidence": 0.0, "reason": ""}

# def check_evolution(last_stage: str, current_result: dict) -> str:
#     """
#     Checks if the user has evolved to a higher Spiral Dynamics stage compared
#     to last_stage. Returns a level-up message or None.
#     """
#     if not last_stage:
#         return None
#     current_stage = current_result.get("stage", "Unknown")
#     try:
#         last_index = STAGES.index(last_stage)
#         current_index = STAGES.index(current_stage)
#         confidence = current_result.get("confidence", 0)
#         if current_index > last_index and confidence >= 0.6:
#             return f"🌱 Level Up! You're showing strong {current_stage} tendencies!"
#     except ValueError:
#         pass
# #     return None
# import json
# from openai import OpenAI
# from config import A4F_API_KEY

# STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

# # Meta information for gamified prompts - must be defined elsewhere or here
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

# client = OpenAI(api_key=A4F_API_KEY, base_url="https://api.a4f.co/v1")


# def detect_intent(entry):
#     prompt = (
#         "You are a Spiral Dynamics gatekeeper.\n"
#         "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
#         "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
#         f"Entry: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="provider-3/gpt-4",  # or "provider-3/gpt-4o"
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0,
#     )
#     return "spiral" if "spiral" in response.choices[0].message.content.lower() else "chat"


# # def detect_intent(entry: str) -> str:
# #     """
# #     Detect if the journal entry reflects Spiral Dynamics depth (spiral) or casual chat.
# #     Returns 'spiral' or 'chat'.
# #     """
# #     prompt = (
# #         "You are a Spiral Dynamics gatekeeper.\n"
# #         "Determine if the entry is deep personal reflection or casual conversation.\n"
# #         "Respond 'spiral' for deep reflection, 'chat' for casual.\n"
# #         f"Entry: \"{entry}\""
# #     )
# #     response = client.chat.completions.create(
# #         model="provider-3/gpt-4",
# #         messages=[{"role": "user", "content": prompt}],
# #         temperature=0,
# #     )
# #     content = response.choices[0].message.content.lower()
# #     return "spiral" if "spiral" in content else "chat"

# # def classify_stage(entry: str) -> dict:
# #     """
# #     Classify the Spiral Dynamics stage of the entry.
# #     Returns dict with keys: 'stage', 'secondary', 'confidence', 'reason'.
# #     """
# #     prompt = (
# #         f"Classify the following message into one Spiral Dynamics stage from {', '.join(STAGES)}.\n"
# #         "Return JSON with primary stage, secondary stage (if any), confidence (0-1), and reason.\n"
# #         f"Input: \"{entry}\""
# #     )
# #     response = client.chat.completions.create(
# #         model="provider-3/gpt-4",
# #         messages=[{"role": "user", "content": prompt}],
# #         temperature=0.3,
# #         response_format={"type": "json_object"},
# #     )
# #     try:
# #         data = json.loads(response.choices[0].message.content)
# #         return {
# #             "stage": data.get("primary_stage", "Unknown"),
# #             "secondary": data.get("secondary_stage"),
# #             "confidence": float(data.get("confidence", 0)),
# #             "reason": data.get("reason", ""),
# #         }
# #     except Exception:
# #         fallback = client.chat.completions.create(
# #             model="provider-3/gpt-4",
# #             messages=[{"role": "user", "content": f"Classify into one stage: {entry}"}],
# #             temperature=0,
# #         )
# #         return {"stage": fallback.choices[0].message.content.strip(), "secondary": None, "confidence": 1.0, "reason": ""}


# def classify_stage(entry):
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
#         model="provider-3/gpt-4",
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
#     except:
#         # Fallback to simple classification if JSON parsing fails
#         simple_response = client.chat.completions.create(
#             model="provider-3/gpt-4",
#             messages=[{"role": "user", "content": f"Classify this into one stage from {', '.join(STAGES)}: {entry}"}],
#             temperature=0
#         )
#         return {
#             "stage": simple_response.choices[0].message.content.strip(),
#             "secondary": None,
#             "confidence": 1.0,
#             "reason": ""
#         }


# def check_evolution(last_stage: str, current_result: dict) -> str:
#     """
#     Return an evolution message if user evolved to a higher stage.
#     Otherwise, return None.
#     """
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


# def generate_reflective_question(entry, reply_to=None):
#     context = f"\nReplying to: \"{reply_to}\"" if reply_to else ""
#     prompt = (
#         f"You are a Spiral Dynamics mentor. Based on the user's thoughts{context}, "
#         f"ask one deep, emotionally resonant question (max 15 words). Just ask the question.\n\n"
#         f"User message: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.85,
#     )
#     return response.choices[0].message.content.strip()


# def generate_gamified_prompt(stage, entry, evolution=False):
#     """Generate dynamic gamified prompts based on stage and evolution status"""
#     stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
    
#     # Generate context-aware prompt based on stage and user input
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
#         model="provider-3/gpt-4",  # or "provider-3/gpt-4o"
#         messages=[{"role": "user", "content": prompt_template}],
#         temperature=0.7,
#         response_format={"type": "json_object"}
#     )
    
#     try:
#         content = json.loads(response.choices[0].message.content)
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {content['question']}",
#             "gamified_prompt": f"💡 {content['prompt']}",
#             "reward": content['reward'] if evolution else stage_meta["reward"]
#         }
#     except:
#         # Fallback if JSON parsing fails
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What about this resonates most with you?",
#             "gamified_prompt": "💡 Reflect on how this shows up in your daily life",
#             "reward": stage_meta["reward"]
#         }




# def generate_reflective_question(entry: str, reply_to: str = None) -> str:
#     context = f"\nReplying to: \"{reply_to}\"" if reply_to else ""
#     prompt = (
#         f"You are a Spiral Dynamics mentor.\n"
#         f"Ask one deep, emotionally resonant question (max 15 words) based on this user input{context}.\n"
#         f"User input: \"{entry}\""
#     )
#     response = client.chat.completions.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.85,
#     )
#     return response.choices[0].message.content.strip()

# def generate_gamified_prompt(stage: str, entry: str, evolution: bool = False) -> dict:
#     stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
#     prompt = (
#         f"Create a gamified interaction for a user at stage {stage} based on input: {entry}.\n"
#         "Provide a JSON containing:\n"
#         "- question (5-10 words)\n"
#         "- a concrete action prompt (max 15 words)\n"
#         "- a reward description\n"
#         "Format: {\"question\": ..., \"prompt\": ..., \"reward\": ...}"
#     )
#     response = client.chat.completions.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.7,
#         response_format={"type": "json_object"},
#     )
#     try:
#         data = json.loads(response.choices[0].message.content)
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {data.get('question', '')}",
#             "gamified_prompt": f"💡 {data.get('prompt', '')}",
#             "reward": data.get('reward', stage_meta['reward']) if evolution else stage_meta['reward'],
#         }
#     except Exception:
#         return {
#             "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What resonates most with you?",
#             "gamified_prompt": "💡 Reflect on how this applies to your life",
#             "reward": stage_meta['reward'],
#         }