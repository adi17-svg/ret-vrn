
# from flask import Blueprint, request, jsonify, Response, current_app
# import os
# import time
# from urllib.parse import quote_plus
# from google.cloud import firestore #new import 
# from tools.tool_registry import get_tool #new import


# from spiral_dynamics import (
#     detect_intent,
#     classify_stage,
#     check_evolution,
#     generate_reflective_question,
#     generate_gamified_prompt,
#     client,
# )
# from firebase_utils import (
#     db,
#     save_conversation_message,
#     get_recent_conversation,
# )
# from tts import stream_tts_from_openai
# from tools.tool_runner import run_tool


# bp = Blueprint("main", __name__)

# HISTORY_LIMIT = 6
# AUDIO_FOLDER = "audios"
# os.makedirs(AUDIO_FOLDER, exist_ok=True)

# DYSREGULATED_MOODS = {
#     "angry", "sad", "anxious", "overwhelmed",
#     "confused", "stressed", "tired",
# }

# # this is new if necessary then remove or let it be
# SPIRAL_ORDER = [
#     "Beige",
#     "Purple",
#     "Red",
#     "Blue",
#     "Orange",
#     "Green",
#     "Yellow",
#     "Turquoise",
# ]

# def compare_spiral_levels(prev: str | None, current: str | None):
#     if not prev or not current:
#         return "unknown"

#     try:
#         p = SPIRAL_ORDER.index(prev)
#         c = SPIRAL_ORDER.index(current)
#     except ValueError:
#         return "unknown"

#     if c > p:
#         return "up"
#     elif c < p:
#         return "down"
#     return "same"


# # ======================================================
# # 🧠 RESPONSE STYLE DECIDER (Wysa-style)
# # ======================================================
# def decide_response_type(mood: str | None, intent: str) -> str:
#     if intent == "chat":
#         return "listen"
#     if mood in {"sad", "anxious", "overwhelmed", "tired", "stressed"}:
#         return "validate"
#     if mood in {"confused", "stuck", "uncertain"}:
#         return "reflect"
#     return "act"


# # ======================================================
# # 🧠 SINGLE BRAIN (TEXT → RESPONSE)
# # ======================================================
# # def process_reflection_core(
# #     entry: str,
# #     user_id: str | None,
# #     last_stage: str = "",
# #     reply_to: str = "",
# # ):
# #     """
# #     THE ONLY PLACE WHERE THINKING HAPPENS
# #     """

# #     # 1️⃣ User support focus (soft bias only)
# #     support_focus = []
# #     if user_id:
# #         try:
# #             doc = db.collection("users").document(user_id).get()
# #             if doc.exists:
# #                 support_focus = doc.to_dict().get("support_focus", [])
# #         except Exception:
# #             pass

# #     # 2️⃣ Intent + Spiral classification (INTERNAL)
# #     intent = detect_intent(entry)

# #     mood = None
# #     stage = None
# #     confidence = 0.0

# #     try:
# #         result = classify_stage(entry)
# #         mood = result.get("mood")
# #         stage = result.get("stage")
# #         confidence = result.get("confidence", 0.0)
# #     except Exception:
# #         pass

# #     # 3️⃣ Decide response tone (Wysa rule)
# #     response_type = decide_response_type(mood, intent)

# #     # 4️⃣ Spiral guardrail (HIDDEN)
# #     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
# #     if len(entry.split()) < 4:
# #         spiral_active = False

# #     # 5️⃣ Context memory
# #     context_messages = []
# #     if user_id:
# #         try:
# #             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
# #             for m in recent:
# #                 if m.get("role") in ("user", "assistant"):
# #                     context_messages.append(
# #                         {"role": m["role"], "content": m["content"]}
# #                     )
# #         except Exception:
# #             pass

# #     # 6️⃣ Mind mirror vs mission
# #     question = None
# #     mission = None

# #     if response_type in {"validate", "reflect"}:
# #         try:
# #             question = generate_reflective_question(entry, reply_to)
# #         except Exception:
# #             pass

# #     if response_type == "act" and spiral_active:
# #         try:
# #             gamified = generate_gamified_prompt(stage, entry)
# #             mission = gamified.get("gamified_prompt")
# #         except Exception:
# #             pass

# #     # 7️⃣ Evolution (growth only, not chat)
# #     evolution_msg = None
# #     if spiral_active and last_stage:
# #         evolution_msg = check_evolution(
# #             last_stage,
# #             {"stage": stage, "confidence": confidence},
# #         )

# #     # 8️⃣ System prompt (language control only)
# #     system_prompt = (
# #         "You are a warm, grounded companion in the RETVRN app.\n\n"
# #         f"Response tone: {response_type}\n\n"
# #         "Rules:\n"
# #         "- Validate emotions first\n"
# #         "- Slow the pace\n"
# #         "- Keep sentences short\n"
# #         "- Never force action\n"
# #         "- Offer choice gently\n\n"
# #         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
# #     )

# #     if question:
# #         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

# #     if mission:
# #         system_prompt += (
# #             "\nOffer this only if the user agrees:\n"
# #             f"{mission}\n"
# #         )

# #     # 9️⃣ GPT CALL (ONLY PLACE)
# #     messages = [
# #         {"role": "system", "content": system_prompt},
# #         *context_messages,
# #         {"role": "user", "content": entry},
# #     ]

# #     resp = client.chat.completions.create(
# #         model="gpt-4.1",
# #         messages=messages,
# #         temperature=0.7,
# #     )

# #     ai_text = resp.choices[0].message.content.strip()

# #     # 🔟 Save memory
# #     if user_id:
# #         try:
# #             save_conversation_message(user_id, "user", entry)
# #             save_conversation_message(user_id, "assistant", ai_text)
# #         except Exception:
# #             pass

# #     # ✅ Unified response
# #     return {
# #         "message": {
# #             "text": ai_text,
# #             "tone": response_type,
# #         },
# #         "reflection": {
# #             "mind_mirror": question,
# #         },
# #         "action": {
# #             "mission": mission,
# #             "requires_permission": True if mission else False,
# #         },
# #         "pattern": {
# #             "stage": stage if spiral_active else None,
# #             "evolution": evolution_msg,
# #         },
# #     }


# # def process_reflection_core(
# #     entry: str,
# #     user_id: str | None,
# #     last_stage: str = "",
# #     reply_to: str = "",
# # ):
# #     """
# #     THE ONLY PLACE WHERE THINKING HAPPENS
# #     """

# #     # 1️⃣ User support focus (soft bias only)
# #     support_focus = []
# #     if user_id:
# #         try:
# #             doc = db.collection("users").document(user_id).get()
# #             if doc.exists:
# #                 support_focus = doc.to_dict().get("support_focus", [])
# #         except Exception:
# #             pass

# #     # 2️⃣ Intent + Spiral classification (INTERNAL)
# #     intent = detect_intent(entry)

# #     mood = None
# #     stage = None
# #     confidence = 0.0

# #     try:
# #         result = classify_stage(entry)
# #         mood = result.get("mood")
# #         stage = result.get("stage")
# #         confidence = result.get("confidence", 0.0)
# #     except Exception:
# #         pass

# #     # 3️⃣ Decide response tone (Wysa rule)
# #     response_type = decide_response_type(mood, intent)

# #     # 🔧 CHANGE 1: Soft bias for gratitude notification replies
# #     if reply_to == "gratitude_prompt":
# #         response_type = "listen"

# #     # 4️⃣ Spiral guardrail (HIDDEN)
# #     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
# #     if len(entry.split()) < 4:
# #         spiral_active = False

# #     # 5️⃣ Context memory
# #     context_messages = []
# #     if user_id:
# #         try:
# #             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
# #             for m in recent:
# #                 if m.get("role") in ("user", "assistant"):
# #                     context_messages.append(
# #                         {"role": m["role"], "content": m["content"]}
# #                     )
# #         except Exception:
# #             pass

# #     # 6️⃣ Mind mirror vs mission
# #     question = None
# #     mission = None

# #     if response_type in {"validate", "reflect"}:
# #         try:
# #             question = generate_reflective_question(entry, reply_to)
# #         except Exception:
# #             pass

# #     if response_type == "act" and spiral_active:
# #         try:
# #             gamified = generate_gamified_prompt(stage, entry)
# #             mission = gamified.get("gamified_prompt")
# #         except Exception:
# #             pass

# #     # 7️⃣ Evolution (growth only, not chat)
# #     evolution_msg = None
# #     if spiral_active and last_stage:
# #         evolution_msg = check_evolution(
# #             last_stage,
# #             {"stage": stage, "confidence": confidence},
# #         )

# #     # 8️⃣ System prompt (language control only)
# #     system_prompt = (
# #         "You are a warm, grounded companion in the RETVRN app.\n\n"
# #         f"Response tone: {response_type}\n\n"
# #         "Rules:\n"
# #         "- Validate emotions first\n"
# #         "- Slow the pace\n"
# #         "- Keep sentences short\n"
# #         "- Never force action\n"
# #         "- Offer choice gently\n\n"
# #         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
# #     )

# #     if question:
# #         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

# #     if mission:
# #         system_prompt += (
# #             "\nOffer this only if the user agrees:\n"
# #             f"{mission}\n"
# #         )

# #     # 9️⃣ GPT CALL (ONLY PLACE)
# #     messages = [
# #         {"role": "system", "content": system_prompt},
# #         *context_messages,
# #         {"role": "user", "content": entry},
# #     ]

# #     resp = client.chat.completions.create(
# #         model="gpt-4.1",
# #         messages=messages,
# #         temperature=0.7,
# #     )

# #     ai_text = resp.choices[0].message.content.strip()

# #     # 🔟 Save memory
# #     if user_id:
# #         try:
# #             # 🔧 CHANGE 2 (OPTIONAL, SAFE):
# #             # If your save_conversation_message supports metadata, you can extend it.
# #             save_conversation_message(
# #                 user_id,
# #                 "user",
# #                 entry,
# #                 # meta={
# #                 #     "reply_to": reply_to,
# #                 # }
# #             )
# #             save_conversation_message(user_id, "assistant", ai_text)
# #         except Exception:
# #             pass

# #     # ✅ Unified response
# #     return {
# #         "message": {
# #             "text": ai_text,
# #             "tone": response_type,
# #         },
# #         "reflection": {
# #             "mind_mirror": question,
# #         },
# #         "action": {
# #             "mission": mission,
# #             "requires_permission": True if mission else False,
# #         },
# #         "pattern": {
# #             "stage": stage if spiral_active else None,
# #             "evolution": evolution_msg,
# #         },
# #     }

# # def process_reflection_core(
# #     entry: str,
# #     user_id: str | None,
# #     last_stage: str = "",
# #     reply_to: str = "",
# # ):
# #     """
# #     THE ONLY PLACE WHERE THINKING HAPPENS
# #     """

# #     # 1️⃣ User support focus (soft bias only)
# #     support_focus = []
# #     if user_id:
# #         try:
# #             doc = db.collection("users").document(user_id).get()
# #             if doc.exists:
# #                 support_focus = doc.to_dict().get("support_focus", [])
# #         except Exception:
# #             pass

# #     # 2️⃣ Intent + Spiral classification (INTERNAL)
# #     intent = detect_intent(entry)

# #     mood = None
# #     stage = None
# #     confidence = 0.0

# #     try:
# #         result = classify_stage(entry)
# #         mood = result.get("mood")
# #         stage = result.get("stage")
# #         confidence = result.get("confidence", 0.0)
# #     except Exception:
# #         pass

# #     # 3️⃣ Decide response tone (Wysa rule)
# #     response_type = decide_response_type(mood, intent)

# #     if reply_to == "gratitude_prompt":
# #         response_type = "listen"

# #     # 4️⃣ Spiral guardrail
# #     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
# #     if len(entry.split()) < 4:
# #         spiral_active = False

# #     # 🔄 Spiral tracking (kami / jasta + history)
# #     direction = "unknown"
# #     previous_stage = None

# #     if user_id and stage:
# #         user_ref = db.collection("users").document(user_id)
# #         snap = user_ref.get()

# #         if snap.exists:
# #             previous_stage = snap.to_dict().get("last_spiral_stage")

# #         direction = compare_spiral_levels(previous_stage, stage)

# #         user_ref.set(
# #             {
# #                 "last_spiral_stage": stage,
# #                 "last_confidence": confidence,
# #                 "updated_at": firestore.SERVER_TIMESTAMP,
# #             },
# #             merge=True,
# #         )

# #         if spiral_active:
# #             user_ref.collection("mergedMessages").add(
# #                 {
# #                     "type": "spiral",
# #                     "stage": stage,
# #                     "confidence": confidence,
# #                     "timestamp": firestore.SERVER_TIMESTAMP,
# #                 }
# #             )

# #     # 5️⃣ Context memory
# #     context_messages = []
# #     if user_id:
# #         try:
# #             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
# #             for m in recent:
# #                 if m.get("role") in ("user", "assistant"):
# #                     context_messages.append(
# #                         {"role": m["role"], "content": m["content"]}
# #                     )
# #         except Exception:
# #             pass

# #     # 6️⃣ Mind mirror vs mission
# #     question = None
# #     mission = None

# #     if response_type in {"validate", "reflect"}:
# #         try:
# #             question = generate_reflective_question(entry, reply_to)
# #         except Exception:
# #             pass

# #     if response_type == "act" and spiral_active:
# #         try:
# #             gamified = generate_gamified_prompt(stage, entry)
# #             mission = gamified.get("gamified_prompt")
# #         except Exception:
# #             pass

# #     # 7️⃣ System prompt
# #     system_prompt = (
# #         "You are a warm, grounded companion in the RETVRN app.\n\n"
# #         f"Response tone: {response_type}\n\n"
# #         "Rules:\n"
# #         "- Validate emotions first\n"
# #         "- Slow the pace\n"
# #         "- Keep sentences short\n"
# #         "- Never force action\n"
# #         "- Offer choice gently\n\n"
# #         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
# #     )

# #     if question:
# #         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

# #     if mission:
# #         system_prompt += f"\nOffer this only if the user agrees:\n{mission}\n"

# #     # 8️⃣ GPT CALL
# #     messages = [
# #         {"role": "system", "content": system_prompt},
# #         *context_messages,
# #         {"role": "user", "content": entry},
# #     ]

# #     resp = client.chat.completions.create(
# #         model="gpt-4.1",
# #         messages=messages,
# #         temperature=0.7,
# #     )

# #     ai_text = resp.choices[0].message.content.strip()

# #     # 9️⃣ Save memory
# #     if user_id:
# #         try:
# #             save_conversation_message(user_id, "user", entry)
# #             save_conversation_message(user_id, "assistant", ai_text)
# #         except Exception:
# #             pass

# #     # ✅ FINAL unified response
# #     return {
# #         "message": {
# #             "text": ai_text,
# #             "tone": response_type,
# #         },
# #         "reflection": {
# #             "mind_mirror": question,
# #         },
# #         "action": {
# #             "mission": mission,
# #             "requires_permission": True if mission else False,
# #         },
# #         "pattern": {
# #             "stage": stage if spiral_active else None,
# #         },
# #         "spiral_tracking": {
# #             "current_stage": stage,
# #             "previous_stage": previous_stage,
# #             "direction": direction,
# #             "confidence": confidence,
# #         },
# #     }

# # def process_reflection_core(
# #     entry: str,
# #     user_id: str | None,
# #     last_stage: str = "",
# #     reply_to: str = "",
# #     tool_id: str | None = None,   # ✅ NEW (OPTIONAL)
# # ):
# #     """
# #     THE ONLY PLACE WHERE THINKING HAPPENS
# #     """

# #     # 1️⃣ User support focus (soft bias only)
# #     support_focus = []
# #     if user_id:
# #         try:
# #             doc = db.collection("users").document(user_id).get()
# #             if doc.exists:
# #                 support_focus = doc.to_dict().get("support_focus", [])
# #         except Exception:
# #             pass

# #     # 2️⃣ Intent + Spiral classification (INTERNAL)
# #     intent = detect_intent(entry)

# #     mood = None
# #     stage = None
# #     confidence = 0.0

# #     try:
# #         result = classify_stage(entry)
# #         mood = result.get("mood")
# #         stage = result.get("stage")
# #         confidence = result.get("confidence", 0.0)
# #     except Exception:
# #         pass

# #     # 3️⃣ Decide response tone (Wysa rule)
# #     response_type = decide_response_type(mood, intent)

# #     if reply_to == "gratitude_prompt":
# #         response_type = "listen"

# #     # 4️⃣ Spiral guardrail
# #     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
# #     if len(entry.split()) < 4:
# #         spiral_active = False

# #     # 🚫 TOOL MODE → spiral / growth OFF
# #     if tool_id:
# #         spiral_active = False
# #         response_type = "listen"   # ✅ ADD THIS LINE

# #     # 🔄 Spiral tracking (ONLY for main chat)
# #     direction = "unknown"
# #     previous_stage = None

# #     if user_id and stage and not tool_id:
# #         user_ref = db.collection("users").document(user_id)
# #         snap = user_ref.get()

# #         if snap.exists:
# #             previous_stage = snap.to_dict().get("last_spiral_stage")

# #         direction = compare_spiral_levels(previous_stage, stage)

# #         user_ref.set(
# #             {
# #                 "last_spiral_stage": stage,
# #                 "last_confidence": confidence,
# #                 "updated_at": firestore.SERVER_TIMESTAMP,
# #             },
# #             merge=True,
# #         )

# #         if spiral_active:
# #             user_ref.collection("mergedMessages").add(
# #                 {
# #                     "type": "spiral",
# #                     "stage": stage,
# #                     "confidence": confidence,
# #                     "timestamp": firestore.SERVER_TIMESTAMP,
# #                 }
# #             )

# #     # 5️⃣ Context memory
# #     context_messages = []
# #     if user_id:
# #         try:
# #             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
# #             for m in recent:
# #                 if m.get("role") in ("user", "assistant"):
# #                     context_messages.append(
# #                         {"role": m["role"], "content": m["content"]}
# #                     )
# #         except Exception:
# #             pass

# #     # 6️⃣ Mind mirror vs mission
# #     question = None
# #     mission = None

# #     if response_type in {"validate", "reflect"}:
# #         try:
# #             question = generate_reflective_question(entry, reply_to)
# #         except Exception:
# #             pass

# #     if response_type == "act" and spiral_active:
# #         try:
# #             gamified = generate_gamified_prompt(stage, entry)
# #             mission = gamified.get("gamified_prompt")
# #         except Exception:
# #             pass
    
      
# #     # 🚨 TOOL MODE OVERRIDE — RUN TOOL INSTEAD OF GPT
# #     if tool_id:
# #         tool_response = run_tool(tool_id)

# #         if tool_response:
# #             if user_id:
# #                 try:
# #                     save_conversation_message(user_id, "user", entry)
# #                     save_conversation_message(
# #                         user_id,
# #                         "assistant",
# #                         tool_response.get("text", ""),
# #                     )
# #                 except Exception:
# #                     pass

# #             return {
# #                 "message": {
# #                     "text": tool_response["text"],
# #                     "tone": "listen",
# #                 },
# #                 "reflection": {},
# #                 "action": {},
# #                 "pattern": {},
# #                 "spiral_tracking": {},
# #             }
# #     # 7️⃣ System prompt
# #     system_prompt = (
# #         "You are a warm, grounded companion in the RETVRN app.\n\n"
# #         f"Response tone: {response_type}\n\n"
# #         "Rules:\n"
# #         "- Validate emotions first\n"
# #         "- Slow the pace\n"
# #         "- Keep sentences short\n"
# #         "- Never force action\n"
# #         "- Offer choice gently\n\n"
# #         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
# #     )

# #     if question:
# #         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

# #     if mission:
# #         system_prompt += f"\nOffer this only if the user agrees:\n{mission}\n"

# #     # 8️⃣ GPT CALL
# #     messages = [
# #         {"role": "system", "content": system_prompt},
# #         *context_messages,
# #         {"role": "user", "content": entry},
# #     ]

# #     resp = client.chat.completions.create(
# #         model="gpt-4.1",
# #         messages=messages,
# #         temperature=0.7,
# #     )

# #     ai_text = resp.choices[0].message.content.strip()

# #     # 9️⃣ Save memory (chat history only, safe for tools too)
# #     if user_id:
# #         try:
# #             save_conversation_message(user_id, "user", entry)
# #             save_conversation_message(user_id, "assistant", ai_text)
# #         except Exception:
# #             pass

# #     # ✅ FINAL unified response
# #     return {
# #         "message": {
# #             "text": ai_text,
# #             "tone": response_type,
# #         },
# #         "reflection": {
# #             "mind_mirror": question,
# #         },
# #         "action": {
# #             "mission": mission,
# #             "requires_permission": True if mission else False,
# #         },
# #         "pattern": {
# #             "stage": stage if spiral_active else None,
# #         },
# #         "spiral_tracking": {
# #             "current_stage": stage if not tool_id else None,
# #             "previous_stage": previous_stage,
# #             "direction": direction,
# #             "confidence": confidence,
# #         },
# #     }

# def process_reflection_core(
#     entry: str,
#     user_id: str | None,
#     last_stage: str = "",
#     reply_to: str = "",
#     tool_id: str | None = None,
# ):
#     """
#     THE ONLY PLACE WHERE THINKING HAPPENS
#     """

#     # 1️⃣ User support focus
#     support_focus = []
#     if user_id:
#         try:
#             doc = db.collection("users").document(user_id).get()
#             if doc.exists:
#                 support_focus = doc.to_dict().get("support_focus", [])
#         except Exception:
#             pass

#     # 2️⃣ Intent + Spiral classification
#     intent = detect_intent(entry)

#     mood = None
#     stage = None
#     confidence = 0.0

#     try:
#         result = classify_stage(entry)
#         mood = result.get("mood")
#         stage = result.get("stage")
#         confidence = result.get("confidence", 0.0)
#     except Exception:
#         pass

#     # 3️⃣ Decide tone
#     response_type = decide_response_type(mood, intent)

#     if reply_to == "gratitude_prompt":
#         response_type = "listen"

#     # 4️⃣ Spiral guardrail
#     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
#     if len(entry.split()) < 4:
#         spiral_active = False

#     # 🚫 TOOL MODE → disable spiral
#     if tool_id:
#         spiral_active = False
#         response_type = "listen"

#     # 🔄 Spiral tracking (main chat only)
#     direction = "unknown"
#     previous_stage = None

#     if user_id and stage and not tool_id:
#         user_ref = db.collection("users").document(user_id)
#         snap = user_ref.get()

#         if snap.exists:
#             previous_stage = snap.to_dict().get("last_spiral_stage")

#         direction = compare_spiral_levels(previous_stage, stage)

#         user_ref.set(
#             {
#                 "last_spiral_stage": stage,
#                 "last_confidence": confidence,
#                 "updated_at": firestore.SERVER_TIMESTAMP,
#             },
#             merge=True,
#         )

#         if spiral_active:
#             user_ref.collection("mergedMessages").add(
#                 {
#                     "type": "spiral",
#                     "stage": stage,
#                     "confidence": confidence,
#                     "timestamp": firestore.SERVER_TIMESTAMP,
#                 }
#             )

#     # 5️⃣ Context memory
#     context_messages = []
#     if user_id:
#         try:
#             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
#             for m in recent:
#                 if m.get("role") in ("user", "assistant"):
#                     context_messages.append(
#                         {"role": m["role"], "content": m["content"]}
#                     )
#         except Exception:
#             pass

#     # 6️⃣ Reflection logic
#     question = None
#     mission = None

#     if response_type in {"validate", "reflect"}:
#         try:
#             question = generate_reflective_question(entry, reply_to)
#         except Exception:
#             pass

#     if response_type == "act" and spiral_active:
#         try:
#             gamified = generate_gamified_prompt(stage, entry)
#             mission = gamified.get("gamified_prompt")
#         except Exception:
#             pass

#     # 🚨 TOOL MODE OVERRIDE
#     if tool_id:
#         tool_response = run_tool(tool_id)

#         if tool_response:
#             if user_id:
#                 try:
#                     save_conversation_message(user_id, "user", entry)
#                     save_conversation_message(
#                         user_id,
#                         "assistant",
#                         tool_response.get("text", ""),
#                     )
#                 except Exception:
#                     pass

#             return {
#                 "message": {
#                     "text": tool_response["text"],
#                     "tone": "listen",
#                 },
#                 "reflection": {},
#                 "action": {},
#                 "pattern": {},
#                 "spiral_tracking": {},
#             }

#     # 7️⃣ System prompt
#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response tone: {response_type}\n\n"
#         "Rules:\n"
#         "- Validate emotions first\n"
#         "- Slow the pace\n"
#         "- Keep sentences short\n"
#         "- Never force action\n"
#         "- Offer choice gently\n\n"
#         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
#     )

#     if question:
#         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

#     if mission:
#         system_prompt += f"\nOffer this only if the user agrees:\n{mission}\n"

#     # 8️⃣ GPT CALL
#     messages = [
#         {"role": "system", "content": system_prompt},
#         *context_messages,
#         {"role": "user", "content": entry},
#     ]

#     resp = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.7,
#     )

#     ai_text = resp.choices[0].message.content.strip()

#     # 🌊 SOFT END BLEND (main chat only)
#     if stage and spiral_active and not tool_id:
#         stage_line = f"\n\n— 🌊 {stage} energy is present in this reflection."
#         ai_text = ai_text + stage_line

#     # 9️⃣ Save memory (after blend)
#     if user_id:
#         try:
#             save_conversation_message(user_id, "user", entry)
#             save_conversation_message(user_id, "assistant", ai_text)
#         except Exception:
#             pass

#     # 🔟 Final response
#     return {
#         "message": {
#             "text": ai_text,
#             "tone": response_type,
#         },
#         "reflection": {
#             "mind_mirror": question,
#         },
#         "action": {
#             "mission": mission,
#             "requires_permission": True if mission else False,
#         },
#         "pattern": {
#             "stage": stage if spiral_active else None,
#         },
#         "spiral_tracking": {
#             "current_stage": stage if not tool_id else None,
#             "previous_stage": previous_stage,
#             "direction": direction,
#             "confidence": confidence,
#         },
#     }

# # ======================================================
# # ROUTES
# # ======================================================
# @bp.route("/")
# def home():
#     return "Backend is running"


# # 🧠 TEXT → RESPONSE (MAIN ENTRY)
# # @bp.route("/merged", methods=["POST"])
# # def merged():
# #     data = request.json or {}
# #     entry = (data.get("text") or "").strip()

# #     if not entry:
# #         return jsonify({"error": "Missing text"}), 400

# #     result = process_reflection_core(
# #         entry=entry,
# #         user_id=data.get("user_id"),
# #         last_stage=data.get("last_stage", ""),
# #         reply_to=data.get("reply_to", ""),
# #     )

# #     # Optional voice reply
# #     audio_url = (
# #         f"{request.url_root.rstrip('/')}"
# #         f"/speak-stream?text={quote_plus(result['message']['text'])}"
# #     )
# #     result["audiourl"] = audio_url

# #     return jsonify(result)

# # @bp.route("/merged", methods=["POST"])
# # def merged():
# #     data = request.json or {}
# #     entry = (data.get("text") or "").strip()

# #     if not entry:
# #         return jsonify({"error": "Missing text"}), 400

# #     # 🔹 NEW (SAFE, OPTIONAL)
# #     tool_id = data.get("tool_id")  # main chat मध्ये None असेल
# #     tool = get_tool(tool_id)   # ✅ ADD THIS

# #     result = process_reflection_core(
# #         entry=entry,
# #         user_id=data.get("user_id"),
# #         last_stage=data.get("last_stage", ""),
# #         reply_to=data.get("reply_to", ""),
# #         tool_id=tool_id,   # 🔹 NEW
# #     )

# #     # Optional voice reply (UNCHANGED)
# #     audio_url = (
# #         f"{request.url_root.rstrip('/')}"
# #         f"/speak-stream?text={quote_plus(result['message']['text'])}"
# #     )
# #     result["audiourl"] = audio_url

# #     return jsonify(result)
# @bp.route("/merged", methods=["POST"])
# def merged():
#     data = request.json or {}

#     entry = (data.get("text") or "").strip()

#     user_id = data.get("user_id")
#     last_stage = data.get("last_stage", "")
#     reply_to = data.get("reply_to", "")

#     # 🔹 TOOL CONTEXT
#     tool_id = data.get("tool_id")          # None for main chat
#     tool_step = data.get("tool_step")      # None on first step

#     # =========================
#     # 🧠 TOOL MODE
#     # =========================
#     if tool_id:
#         tool_response = run_tool(
#             tool_id=tool_id,
#             step=tool_step,
#             user_text=entry or None,   # 👈 allow empty
#         )

#         if not tool_response:
#             return jsonify({"error": "Invalid tool"}), 400

#         # save conversation (optional, safe)
#         if user_id:
#             try:
#                 if entry:
#                     save_conversation_message(user_id, "user", entry)

#                 save_conversation_message(
#                     user_id,
#                     "assistant",
#                     tool_response.get("text", ""),
#                 )
#             except Exception:
#                 pass

#         return jsonify({
#             "message": {
#                 "text": tool_response["text"],
#                 "tone": "listen",
#             },
#             "tool": {
#                 "id": tool_id,
#                 "step": tool_response.get("step"),
#             },
#             "reflection": {},
#             "action": {},
#             "pattern": {},
#             "spiral_tracking": {},
#         })

#     # =========================
#     # 💬 MAIN CHAT (UNCHANGED)
#     # =========================
#     if not entry:
#         return jsonify({"error": "Missing text"}), 400

#     result = process_reflection_core(
#         entry=entry,
#         user_id=user_id,
#         last_stage=last_stage,
#         reply_to=reply_to,
#         tool_id=None,
#     )

#     audio_url = (
#         f"{request.url_root.rstrip('/')}speak-stream"
#         f"?text={quote_plus(result['message']['text'])}"
#     )
#     result["audiourl"] = audio_url

#     return jsonify(result)

# # 👂 AUDIO → TEXT ONLY (NO THINKING)
# @bp.route("/reflect_transcription", methods=["POST"])
# def reflect_transcription():
#     if "audio" not in request.files:
#         return jsonify({"error": "Missing audio"}), 400

#     audio_file = request.files["audio"]
#     path = f"{AUDIO_FOLDER}/{int(time.time())}.wav"
#     audio_file.save(path)

#     with open(path, "rb") as f:
#         transcript = client.audio.transcriptions.create(
#             model="gpt-4o-transcribe",
#             file=f,
#         )

#     text = (transcript.text or "").strip()
#     return jsonify({"text": text})


# # 🔊 TEXT → SPEECH (STREAM)
# @bp.route("/speak-stream", methods=["GET", "POST"])
# def speak_stream():
#     try:
#         if request.method == "GET":
#             txt = request.args.get("text", "") or ""
#         else:
#             body = request.get_json(silent=True) or {}
#             txt = body.get("text", "") or ""

#         if not txt.strip():
#             return jsonify({"error": "missing text"}), 400

#         generator = stream_tts_from_openai(txt)
#         return Response(
#             generator,
#             mimetype="audio/mpeg",
#             direct_passthrough=True,
#         )

#     except Exception as e:
#         current_app.logger.exception(f"TTS error: {e}")
#         return jsonify({"error": "Internal server error"}), 500

from flask import Blueprint, request, jsonify, Response, current_app
import os
import time
from urllib.parse import quote_plus
from google.cloud import firestore #new import 
from tools.tool_registry import get_tool #new import


from spiral_dynamics import (
    detect_intent,
    classify_stage,
    check_evolution,
    generate_reflective_question,
    generate_gamified_prompt,
    client,
)
from firebase_utils import (
    db,
    save_conversation_message,
    get_recent_conversation,
)
from tts import stream_tts_from_openai
from tools.tool_runner import run_tool


bp = Blueprint("main", __name__)

HISTORY_LIMIT = 6
AUDIO_FOLDER = "audios"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

DYSREGULATED_MOODS = {
    "angry", "sad", "anxious", "overwhelmed",
    "confused", "stressed", "tired",
}

# this is new if necessary then remove or let it be
SPIRAL_ORDER = [
    "Beige",
    "Purple",
    "Red",
    "Blue",
    "Orange",
    "Green",
    "Yellow",
    "Turquoise",
]

def compare_spiral_levels(prev: str | None, current: str | None):
    if not prev or not current:
        return "unknown"

    try:
        p = SPIRAL_ORDER.index(prev)
        c = SPIRAL_ORDER.index(current)
    except ValueError:
        return "unknown"

    if c > p:
        return "up"
    elif c < p:
        return "down"
    return "same"


# ======================================================
# 🧠 RESPONSE STYLE DECIDER (Wysa-style)
# ======================================================
def decide_response_type(mood: str | None, intent: str) -> str:
    if intent == "chat":
        return "listen"
    if mood in {"sad", "anxious", "overwhelmed", "tired", "stressed"}:
        return "validate"
    if mood in {"confused", "stuck", "uncertain"}:
        return "reflect"
    return "act"


# ======================================================
# 🧠 SINGLE BRAIN (TEXT → RESPONSE)
# ======================================================
# def process_reflection_core(
#     entry: str,
#     user_id: str | None,
#     last_stage: str = "",
#     reply_to: str = "",
# ):
#     """
#     THE ONLY PLACE WHERE THINKING HAPPENS
#     """

#     # 1️⃣ User support focus (soft bias only)
#     support_focus = []
#     if user_id:
#         try:
#             doc = db.collection("users").document(user_id).get()
#             if doc.exists:
#                 support_focus = doc.to_dict().get("support_focus", [])
#         except Exception:
#             pass

#     # 2️⃣ Intent + Spiral classification (INTERNAL)
#     intent = detect_intent(entry)

#     mood = None
#     stage = None
#     confidence = 0.0

#     try:
#         result = classify_stage(entry)
#         mood = result.get("mood")
#         stage = result.get("stage")
#         confidence = result.get("confidence", 0.0)
#     except Exception:
#         pass

#     # 3️⃣ Decide response tone (Wysa rule)
#     response_type = decide_response_type(mood, intent)

#     # 4️⃣ Spiral guardrail (HIDDEN)
#     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
#     if len(entry.split()) < 4:
#         spiral_active = False

#     # 5️⃣ Context memory
#     context_messages = []
#     if user_id:
#         try:
#             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
#             for m in recent:
#                 if m.get("role") in ("user", "assistant"):
#                     context_messages.append(
#                         {"role": m["role"], "content": m["content"]}
#                     )
#         except Exception:
#             pass

#     # 6️⃣ Mind mirror vs mission
#     question = None
#     mission = None

#     if response_type in {"validate", "reflect"}:
#         try:
#             question = generate_reflective_question(entry, reply_to)
#         except Exception:
#             pass

#     if response_type == "act" and spiral_active:
#         try:
#             gamified = generate_gamified_prompt(stage, entry)
#             mission = gamified.get("gamified_prompt")
#         except Exception:
#             pass

#     # 7️⃣ Evolution (growth only, not chat)
#     evolution_msg = None
#     if spiral_active and last_stage:
#         evolution_msg = check_evolution(
#             last_stage,
#             {"stage": stage, "confidence": confidence},
#         )

#     # 8️⃣ System prompt (language control only)
#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response tone: {response_type}\n\n"
#         "Rules:\n"
#         "- Validate emotions first\n"
#         "- Slow the pace\n"
#         "- Keep sentences short\n"
#         "- Never force action\n"
#         "- Offer choice gently\n\n"
#         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
#     )

#     if question:
#         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

#     if mission:
#         system_prompt += (
#             "\nOffer this only if the user agrees:\n"
#             f"{mission}\n"
#         )

#     # 9️⃣ GPT CALL (ONLY PLACE)
#     messages = [
#         {"role": "system", "content": system_prompt},
#         *context_messages,
#         {"role": "user", "content": entry},
#     ]

#     resp = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.7,
#     )

#     ai_text = resp.choices[0].message.content.strip()

#     # 🔟 Save memory
#     if user_id:
#         try:
#             save_conversation_message(user_id, "user", entry)
#             save_conversation_message(user_id, "assistant", ai_text)
#         except Exception:
#             pass

#     # ✅ Unified response
#     return {
#         "message": {
#             "text": ai_text,
#             "tone": response_type,
#         },
#         "reflection": {
#             "mind_mirror": question,
#         },
#         "action": {
#             "mission": mission,
#             "requires_permission": True if mission else False,
#         },
#         "pattern": {
#             "stage": stage if spiral_active else None,
#             "evolution": evolution_msg,
#         },
#     }


# def process_reflection_core(
#     entry: str,
#     user_id: str | None,
#     last_stage: str = "",
#     reply_to: str = "",
# ):
#     """
#     THE ONLY PLACE WHERE THINKING HAPPENS
#     """

#     # 1️⃣ User support focus (soft bias only)
#     support_focus = []
#     if user_id:
#         try:
#             doc = db.collection("users").document(user_id).get()
#             if doc.exists:
#                 support_focus = doc.to_dict().get("support_focus", [])
#         except Exception:
#             pass

#     # 2️⃣ Intent + Spiral classification (INTERNAL)
#     intent = detect_intent(entry)

#     mood = None
#     stage = None
#     confidence = 0.0

#     try:
#         result = classify_stage(entry)
#         mood = result.get("mood")
#         stage = result.get("stage")
#         confidence = result.get("confidence", 0.0)
#     except Exception:
#         pass

#     # 3️⃣ Decide response tone (Wysa rule)
#     response_type = decide_response_type(mood, intent)

#     # 🔧 CHANGE 1: Soft bias for gratitude notification replies
#     if reply_to == "gratitude_prompt":
#         response_type = "listen"

#     # 4️⃣ Spiral guardrail (HIDDEN)
#     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
#     if len(entry.split()) < 4:
#         spiral_active = False

#     # 5️⃣ Context memory
#     context_messages = []
#     if user_id:
#         try:
#             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
#             for m in recent:
#                 if m.get("role") in ("user", "assistant"):
#                     context_messages.append(
#                         {"role": m["role"], "content": m["content"]}
#                     )
#         except Exception:
#             pass

#     # 6️⃣ Mind mirror vs mission
#     question = None
#     mission = None

#     if response_type in {"validate", "reflect"}:
#         try:
#             question = generate_reflective_question(entry, reply_to)
#         except Exception:
#             pass

#     if response_type == "act" and spiral_active:
#         try:
#             gamified = generate_gamified_prompt(stage, entry)
#             mission = gamified.get("gamified_prompt")
#         except Exception:
#             pass

#     # 7️⃣ Evolution (growth only, not chat)
#     evolution_msg = None
#     if spiral_active and last_stage:
#         evolution_msg = check_evolution(
#             last_stage,
#             {"stage": stage, "confidence": confidence},
#         )

#     # 8️⃣ System prompt (language control only)
#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response tone: {response_type}\n\n"
#         "Rules:\n"
#         "- Validate emotions first\n"
#         "- Slow the pace\n"
#         "- Keep sentences short\n"
#         "- Never force action\n"
#         "- Offer choice gently\n\n"
#         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
#     )

#     if question:
#         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

#     if mission:
#         system_prompt += (
#             "\nOffer this only if the user agrees:\n"
#             f"{mission}\n"
#         )

#     # 9️⃣ GPT CALL (ONLY PLACE)
#     messages = [
#         {"role": "system", "content": system_prompt},
#         *context_messages,
#         {"role": "user", "content": entry},
#     ]

#     resp = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.7,
#     )

#     ai_text = resp.choices[0].message.content.strip()

#     # 🔟 Save memory
#     if user_id:
#         try:
#             # 🔧 CHANGE 2 (OPTIONAL, SAFE):
#             # If your save_conversation_message supports metadata, you can extend it.
#             save_conversation_message(
#                 user_id,
#                 "user",
#                 entry,
#                 # meta={
#                 #     "reply_to": reply_to,
#                 # }
#             )
#             save_conversation_message(user_id, "assistant", ai_text)
#         except Exception:
#             pass

#     # ✅ Unified response
#     return {
#         "message": {
#             "text": ai_text,
#             "tone": response_type,
#         },
#         "reflection": {
#             "mind_mirror": question,
#         },
#         "action": {
#             "mission": mission,
#             "requires_permission": True if mission else False,
#         },
#         "pattern": {
#             "stage": stage if spiral_active else None,
#             "evolution": evolution_msg,
#         },
#     }

# def process_reflection_core(
#     entry: str,
#     user_id: str | None,
#     last_stage: str = "",
#     reply_to: str = "",
# ):
#     """
#     THE ONLY PLACE WHERE THINKING HAPPENS
#     """

#     # 1️⃣ User support focus (soft bias only)
#     support_focus = []
#     if user_id:
#         try:
#             doc = db.collection("users").document(user_id).get()
#             if doc.exists:
#                 support_focus = doc.to_dict().get("support_focus", [])
#         except Exception:
#             pass

#     # 2️⃣ Intent + Spiral classification (INTERNAL)
#     intent = detect_intent(entry)

#     mood = None
#     stage = None
#     confidence = 0.0

#     try:
#         result = classify_stage(entry)
#         mood = result.get("mood")
#         stage = result.get("stage")
#         confidence = result.get("confidence", 0.0)
#     except Exception:
#         pass

#     # 3️⃣ Decide response tone (Wysa rule)
#     response_type = decide_response_type(mood, intent)

#     if reply_to == "gratitude_prompt":
#         response_type = "listen"

#     # 4️⃣ Spiral guardrail
#     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
#     if len(entry.split()) < 4:
#         spiral_active = False

#     # 🔄 Spiral tracking (kami / jasta + history)
#     direction = "unknown"
#     previous_stage = None

#     if user_id and stage:
#         user_ref = db.collection("users").document(user_id)
#         snap = user_ref.get()

#         if snap.exists:
#             previous_stage = snap.to_dict().get("last_spiral_stage")

#         direction = compare_spiral_levels(previous_stage, stage)

#         user_ref.set(
#             {
#                 "last_spiral_stage": stage,
#                 "last_confidence": confidence,
#                 "updated_at": firestore.SERVER_TIMESTAMP,
#             },
#             merge=True,
#         )

#         if spiral_active:
#             user_ref.collection("mergedMessages").add(
#                 {
#                     "type": "spiral",
#                     "stage": stage,
#                     "confidence": confidence,
#                     "timestamp": firestore.SERVER_TIMESTAMP,
#                 }
#             )

#     # 5️⃣ Context memory
#     context_messages = []
#     if user_id:
#         try:
#             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
#             for m in recent:
#                 if m.get("role") in ("user", "assistant"):
#                     context_messages.append(
#                         {"role": m["role"], "content": m["content"]}
#                     )
#         except Exception:
#             pass

#     # 6️⃣ Mind mirror vs mission
#     question = None
#     mission = None

#     if response_type in {"validate", "reflect"}:
#         try:
#             question = generate_reflective_question(entry, reply_to)
#         except Exception:
#             pass

#     if response_type == "act" and spiral_active:
#         try:
#             gamified = generate_gamified_prompt(stage, entry)
#             mission = gamified.get("gamified_prompt")
#         except Exception:
#             pass

#     # 7️⃣ System prompt
#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response tone: {response_type}\n\n"
#         "Rules:\n"
#         "- Validate emotions first\n"
#         "- Slow the pace\n"
#         "- Keep sentences short\n"
#         "- Never force action\n"
#         "- Offer choice gently\n\n"
#         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
#     )

#     if question:
#         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

#     if mission:
#         system_prompt += f"\nOffer this only if the user agrees:\n{mission}\n"

#     # 8️⃣ GPT CALL
#     messages = [
#         {"role": "system", "content": system_prompt},
#         *context_messages,
#         {"role": "user", "content": entry},
#     ]

#     resp = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.7,
#     )

#     ai_text = resp.choices[0].message.content.strip()

#     # 9️⃣ Save memory
#     if user_id:
#         try:
#             save_conversation_message(user_id, "user", entry)
#             save_conversation_message(user_id, "assistant", ai_text)
#         except Exception:
#             pass

#     # ✅ FINAL unified response
#     return {
#         "message": {
#             "text": ai_text,
#             "tone": response_type,
#         },
#         "reflection": {
#             "mind_mirror": question,
#         },
#         "action": {
#             "mission": mission,
#             "requires_permission": True if mission else False,
#         },
#         "pattern": {
#             "stage": stage if spiral_active else None,
#         },
#         "spiral_tracking": {
#             "current_stage": stage,
#             "previous_stage": previous_stage,
#             "direction": direction,
#             "confidence": confidence,
#         },
#     }

# def process_reflection_core(
#     entry: str,
#     user_id: str | None,
#     last_stage: str = "",
#     reply_to: str = "",
#     tool_id: str | None = None,   # ✅ NEW (OPTIONAL)
# ):
#     """
#     THE ONLY PLACE WHERE THINKING HAPPENS
#     """

#     # 1️⃣ User support focus (soft bias only)
#     support_focus = []
#     if user_id:
#         try:
#             doc = db.collection("users").document(user_id).get()
#             if doc.exists:
#                 support_focus = doc.to_dict().get("support_focus", [])
#         except Exception:
#             pass

#     # 2️⃣ Intent + Spiral classification (INTERNAL)
#     intent = detect_intent(entry)

#     mood = None
#     stage = None
#     confidence = 0.0

#     try:
#         result = classify_stage(entry)
#         mood = result.get("mood")
#         stage = result.get("stage")
#         confidence = result.get("confidence", 0.0)
#     except Exception:
#         pass

#     # 3️⃣ Decide response tone (Wysa rule)
#     response_type = decide_response_type(mood, intent)

#     if reply_to == "gratitude_prompt":
#         response_type = "listen"

#     # 4️⃣ Spiral guardrail
#     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
#     if len(entry.split()) < 4:
#         spiral_active = False

#     # 🚫 TOOL MODE → spiral / growth OFF
#     if tool_id:
#         spiral_active = False
#         response_type = "listen"   # ✅ ADD THIS LINE

#     # 🔄 Spiral tracking (ONLY for main chat)
#     direction = "unknown"
#     previous_stage = None

#     if user_id and stage and not tool_id:
#         user_ref = db.collection("users").document(user_id)
#         snap = user_ref.get()

#         if snap.exists:
#             previous_stage = snap.to_dict().get("last_spiral_stage")

#         direction = compare_spiral_levels(previous_stage, stage)

#         user_ref.set(
#             {
#                 "last_spiral_stage": stage,
#                 "last_confidence": confidence,
#                 "updated_at": firestore.SERVER_TIMESTAMP,
#             },
#             merge=True,
#         )

#         if spiral_active:
#             user_ref.collection("mergedMessages").add(
#                 {
#                     "type": "spiral",
#                     "stage": stage,
#                     "confidence": confidence,
#                     "timestamp": firestore.SERVER_TIMESTAMP,
#                 }
#             )

#     # 5️⃣ Context memory
#     context_messages = []
#     if user_id:
#         try:
#             recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
#             for m in recent:
#                 if m.get("role") in ("user", "assistant"):
#                     context_messages.append(
#                         {"role": m["role"], "content": m["content"]}
#                     )
#         except Exception:
#             pass

#     # 6️⃣ Mind mirror vs mission
#     question = None
#     mission = None

#     if response_type in {"validate", "reflect"}:
#         try:
#             question = generate_reflective_question(entry, reply_to)
#         except Exception:
#             pass

#     if response_type == "act" and spiral_active:
#         try:
#             gamified = generate_gamified_prompt(stage, entry)
#             mission = gamified.get("gamified_prompt")
#         except Exception:
#             pass
    
      
#     # 🚨 TOOL MODE OVERRIDE — RUN TOOL INSTEAD OF GPT
#     if tool_id:
#         tool_response = run_tool(tool_id)

#         if tool_response:
#             if user_id:
#                 try:
#                     save_conversation_message(user_id, "user", entry)
#                     save_conversation_message(
#                         user_id,
#                         "assistant",
#                         tool_response.get("text", ""),
#                     )
#                 except Exception:
#                     pass

#             return {
#                 "message": {
#                     "text": tool_response["text"],
#                     "tone": "listen",
#                 },
#                 "reflection": {},
#                 "action": {},
#                 "pattern": {},
#                 "spiral_tracking": {},
#             }
#     # 7️⃣ System prompt
#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response tone: {response_type}\n\n"
#         "Rules:\n"
#         "- Validate emotions first\n"
#         "- Slow the pace\n"
#         "- Keep sentences short\n"
#         "- Never force action\n"
#         "- Offer choice gently\n\n"
#         f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
#     )

#     if question:
#         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

#     if mission:
#         system_prompt += f"\nOffer this only if the user agrees:\n{mission}\n"

#     # 8️⃣ GPT CALL
#     messages = [
#         {"role": "system", "content": system_prompt},
#         *context_messages,
#         {"role": "user", "content": entry},
#     ]

#     resp = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.7,
#     )

#     ai_text = resp.choices[0].message.content.strip()

#     # 9️⃣ Save memory (chat history only, safe for tools too)
#     if user_id:
#         try:
#             save_conversation_message(user_id, "user", entry)
#             save_conversation_message(user_id, "assistant", ai_text)
#         except Exception:
#             pass

#     # ✅ FINAL unified response
#     return {
#         "message": {
#             "text": ai_text,
#             "tone": response_type,
#         },
#         "reflection": {
#             "mind_mirror": question,
#         },
#         "action": {
#             "mission": mission,
#             "requires_permission": True if mission else False,
#         },
#         "pattern": {
#             "stage": stage if spiral_active else None,
#         },
#         "spiral_tracking": {
#             "current_stage": stage if not tool_id else None,
#             "previous_stage": previous_stage,
#             "direction": direction,
#             "confidence": confidence,
#         },
#     }

def process_reflection_core(
    entry: str,
    user_id: str | None,
    last_stage: str = "",
    reply_to: str = "",
    tool_id: str | None = None,
):
    """
    THE ONLY PLACE WHERE THINKING HAPPENS
    """

    # 1️⃣ User support focus
    support_focus = []
    if user_id:
        try:
            doc = db.collection("users").document(user_id).get()
            if doc.exists:
                support_focus = doc.to_dict().get("support_focus", [])
        except Exception:
            pass

    # 2️⃣ Intent + Spiral classification
    intent = detect_intent(entry)

    mood = None
    stage = None
    confidence = 0.0

    try:
        result = classify_stage(entry)
        mood = result.get("mood")
        stage = result.get("stage")
        confidence = result.get("confidence", 0.0)
    except Exception:
        pass

    # 3️⃣ Decide tone
    response_type = decide_response_type(mood, intent)

    if reply_to == "gratitude_prompt":
        response_type = "listen"

    # 4️⃣ Spiral guardrail
    spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
    if len(entry.split()) < 4:
        spiral_active = False

    # 🚫 TOOL MODE → disable spiral
    if tool_id:
        spiral_active = False
        response_type = "listen"

    # 🔄 Spiral tracking (main chat only)
    direction = "unknown"
    previous_stage = None

    if user_id and stage and not tool_id:
        user_ref = db.collection("users").document(user_id)
        snap = user_ref.get()

        if snap.exists:
            previous_stage = snap.to_dict().get("last_spiral_stage")

        direction = compare_spiral_levels(previous_stage, stage)

        user_ref.set(
            {
                "last_spiral_stage": stage,
                "last_confidence": confidence,
                "updated_at": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )

        if spiral_active:
            user_ref.collection("mergedMessages").add(
                {
                    "type": "spiral",
                    "stage": stage,
                    "confidence": confidence,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                }
            )

    # 5️⃣ Context memory
    context_messages = []
    if user_id:
        try:
            recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
            for m in recent:
                if m.get("role") in ("user", "assistant"):
                    context_messages.append(
                        {"role": m["role"], "content": m["content"]}
                    )
        except Exception:
            pass

    # 6️⃣ Reflection logic
    question = None
    mission = None

    if response_type in {"validate", "reflect"}:
        try:
            question = generate_reflective_question(entry, reply_to)
        except Exception:
            pass

    if response_type == "act" and spiral_active:
        try:
            gamified = generate_gamified_prompt(stage, entry)
            mission = gamified.get("gamified_prompt")
        except Exception:
            pass

    # 🚨 TOOL MODE OVERRIDE
    if tool_id:
        tool_response = run_tool(tool_id)

        if tool_response:
            if user_id:
                try:
                    save_conversation_message(user_id, "user", entry)
                    save_conversation_message(
                        user_id,
                        "assistant",
                        tool_response.get("text", ""),
                    )
                except Exception:
                    pass

            return {
                "message": {
                    "text": tool_response["text"],
                    "tone": "listen",
                },
                "reflection": {},
                "action": {},
                "pattern": {},
                "spiral_tracking": {},
            }

    # 7️⃣ System prompt
    system_prompt = (
        "You are a warm, grounded companion in the RETVRN app.\n\n"
        f"Response tone: {response_type}\n\n"
        "Rules:\n"
        "- Validate emotions first\n"
        "- Slow the pace\n"
        "- Keep sentences short\n"
        "- Never force action\n"
        "- Offer choice gently\n\n"
        f"User support focus (DO NOT mention): {', '.join(support_focus) or 'none'}\n"
    )

    if question:
        system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

    if mission:
        system_prompt += f"\nOffer this only if the user agrees:\n{mission}\n"

    # 8️⃣ GPT CALL
    messages = [
        {"role": "system", "content": system_prompt},
        *context_messages,
        {"role": "user", "content": entry},
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.7,
    )

    ai_text = resp.choices[0].message.content.strip()

    # 🌊 SOFT END BLEND (main chat only)
    if stage and spiral_active and not tool_id:
        stage_line = f"\n\n— 🌊 {stage} energy is present in this reflection."
        ai_text = ai_text + stage_line

    # 9️⃣ Save memory (after blend)
    if user_id:
        try:
            save_conversation_message(user_id, "user", entry)
            save_conversation_message(user_id, "assistant", ai_text)
        except Exception:
            pass

    # 🔟 Final response
    return {
        "message": {
            "text": ai_text,
            "tone": response_type,
        },
        "reflection": {
            "mind_mirror": question,
        },
        "action": {
            "mission": mission,
            "requires_permission": True if mission else False,
        },
        "pattern": {
            "stage": stage if spiral_active else None,
        },
        "spiral_tracking": {
            "current_stage": stage if not tool_id else None,
            "previous_stage": previous_stage,
            "direction": direction,
            "confidence": confidence,
        },
    }

# ======================================================
# ROUTES
# ======================================================
@bp.route("/")
def home():
    return "Backend is running"


# 🧠 TEXT → RESPONSE (MAIN ENTRY)
# @bp.route("/merged", methods=["POST"])
# def merged():
#     data = request.json or {}
#     entry = (data.get("text") or "").strip()

#     if not entry:
#         return jsonify({"error": "Missing text"}), 400

#     result = process_reflection_core(
#         entry=entry,
#         user_id=data.get("user_id"),
#         last_stage=data.get("last_stage", ""),
#         reply_to=data.get("reply_to", ""),
#     )

#     # Optional voice reply
#     audio_url = (
#         f"{request.url_root.rstrip('/')}"
#         f"/speak-stream?text={quote_plus(result['message']['text'])}"
#     )
#     result["audiourl"] = audio_url

#     return jsonify(result)

# @bp.route("/merged", methods=["POST"])
# def merged():
#     data = request.json or {}
#     entry = (data.get("text") or "").strip()

#     if not entry:
#         return jsonify({"error": "Missing text"}), 400

#     # 🔹 NEW (SAFE, OPTIONAL)
#     tool_id = data.get("tool_id")  # main chat मध्ये None असेल
#     tool = get_tool(tool_id)   # ✅ ADD THIS

#     result = process_reflection_core(
#         entry=entry,
#         user_id=data.get("user_id"),
#         last_stage=data.get("last_stage", ""),
#         reply_to=data.get("reply_to", ""),
#         tool_id=tool_id,   # 🔹 NEW
#     )

#     # Optional voice reply (UNCHANGED)
#     audio_url = (
#         f"{request.url_root.rstrip('/')}"
#         f"/speak-stream?text={quote_plus(result['message']['text'])}"
#     )
#     result["audiourl"] = audio_url

#     return jsonify(result)
# @bp.route("/merged", methods=["POST"])
# def merged():
#     data = request.json or {}

#     entry = (data.get("text") or "").strip()

#     user_id = data.get("user_id")
#     last_stage = data.get("last_stage", "")
#     reply_to = data.get("reply_to", "")

#     # 🔹 TOOL CONTEXT
#     tool_id = data.get("tool_id")          # None for main chat
#     tool_step = data.get("tool_step")      # None on first step

#     # =========================
#     # 🧠 TOOL MODE
#     # =========================
#     if tool_id:
#         tool_response = run_tool(
#             tool_id=tool_id,
#             step=tool_step,
#             user_text=entry or None,   # 👈 allow empty
#         )

#         if not tool_response:
#             return jsonify({"error": "Invalid tool"}), 400

#         # save conversation (optional, safe)
#         if user_id:
#             try:
#                 if entry:
#                     save_conversation_message(user_id, "user", entry)

#                 save_conversation_message(
#                     user_id,
#                     "assistant",
#                     tool_response.get("text", ""),
#                 )
#             except Exception:
#                 pass

#         return jsonify({
#             "message": {
#                 "text": tool_response["text"],
#                 "tone": "listen",
#             },
#             "tool": {
#                 "id": tool_id,
#                 "step": tool_response.get("step"),
#             },
#             "reflection": {},
#             "action": {},
#             "pattern": {},
#             "spiral_tracking": {},
#         })

#     # =========================
#     # 💬 MAIN CHAT (UNCHANGED)
#     # =========================
#    # =========================
# # 💬 MAIN CHAT (STREAMING)
# # =========================
#     if not entry:
#         return jsonify({"error": "Missing text"}), 400


#     def generate_stream():

#     # 👉 Rebuild minimal logic here (we cannot use old JSON function directly)

#         support_focus = []
#         if user_id:
#             try:
#                 doc = db.collection("users").document(user_id).get()
#                 if doc.exists:
#                     support_focus = doc.to_dict().get("support_focus", [])
#             except Exception:
#                 pass

#     intent = detect_intent(entry)

#     mood = None
#     stage = None

#     try:
#         result = classify_stage(entry)
#         mood = result.get("mood")
#         stage = result.get("stage")
#     except Exception:
#         pass

#     response_type = decide_response_type(mood, intent)

#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response tone: {response_type}\n\n"
#         "Rules:\n"
#         "- Validate emotions first\n"
#         "- Slow the pace\n"
#         "- Keep sentences short\n"
#         "- Never force action\n"
#         "- Offer choice gently\n"
#     )

#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": entry},
#     ]

#     # 🔥 STREAM ENABLED
#     resp = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.7,
#         stream=True,
#     )

#     full_text = ""

#     for chunk in resp:
#         if chunk.choices[0].delta.content:
#             token = chunk.choices[0].delta.content
#             full_text += token
#             yield token

#     # ✅ After streaming complete → save conversation
#     if user_id:
#         try:
#             save_conversation_message(user_id, "user", entry)
#             save_conversation_message(user_id, "assistant", full_text)
#         except Exception:
#             pass


#     return Response(generate_stream(), mimetype="text/plain")
@bp.route("/merged", methods=["POST"])
def merged():

    # ✅ Always read request FIRST (safe for streaming)
    data = request.get_json(silent=True) or {}

    entry = (data.get("text") or "").strip()
    user_id = data.get("user_id")
    last_stage = data.get("last_stage", "")
    reply_to = data.get("reply_to", "")

    tool_id = data.get("tool_id")
    tool_step = data.get("tool_step")

    # =====================================================
    # 🧠 TOOL MODE (NO STREAMING)
    # =====================================================
    if tool_id:
        tool_response = run_tool(
            tool_id=tool_id,
            step=tool_step,
            user_text=entry or None,
        )

        if not tool_response:
            return jsonify({"error": "Invalid tool"}), 400

        # Save conversation
        if user_id:
            try:
                if entry:
                    save_conversation_message(user_id, "user", entry)

                save_conversation_message(
                    user_id,
                    "assistant",
                    tool_response.get("text", ""),
                )
            except Exception:
                pass

        return jsonify({
            "message": {
                "text": tool_response["text"],
                "tone": "listen",
            },
            "tool": {
                "id": tool_id,
                "step": tool_response.get("step"),
            },
            "reflection": {},
            "action": {},
            "pattern": {},
            "spiral_tracking": {},
        })

    # =====================================================
    # 💬 MAIN CHAT (STREAMING MODE)
    # =====================================================
    if not entry:
        return jsonify({"error": "Missing text"}), 400

    def generate_stream():

        # 🔥 IMPORTANT: DO NOT USE request inside this function

        intent = detect_intent(entry)

        mood = None
        stage = None

        try:
            result = classify_stage(entry)
            mood = result.get("mood")
            stage = result.get("stage")
        except Exception:
            pass

        response_type = decide_response_type(mood, intent)

        system_prompt = (
            "You are a warm, grounded companion in the RETVRN app.\n\n"
            f"Response tone: {response_type}\n\n"
            "- Validate emotions first\n"
            "- Slow the pace\n"
            "- Keep sentences short\n"
            "- Never force action\n"
            "- Offer choice gently\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": entry},
        ]

        resp = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.7,
            stream=True,
        )

        full_text = ""

        for chunk in resp:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_text += token
                yield token

        # ✅ Save after streaming complete
        if user_id:
            try:
                save_conversation_message(user_id, "user", entry)
                save_conversation_message(user_id, "assistant", full_text)
            except Exception:
                pass

    return Response(generate_stream(), mimetype="text/plain")


# 👂 AUDIO → TEXT ONLY (NO THINKING)
@bp.route("/reflect_transcription", methods=["POST"])
def reflect_transcription():
    if "audio" not in request.files:
        return jsonify({"error": "Missing audio"}), 400

    audio_file = request.files["audio"]
    path = f"{AUDIO_FOLDER}/{int(time.time())}.wav"
    audio_file.save(path)

    with open(path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f,
        )

    text = (transcript.text or "").strip()
    return jsonify({"text": text})


# 🔊 TEXT → SPEECH (STREAM)
@bp.route("/speak-stream", methods=["GET", "POST"])
def speak_stream():
    try:
        if request.method == "GET":
            txt = request.args.get("text", "") or ""
        else:
            body = request.get_json(silent=True) or {}
            txt = body.get("text", "") or ""

        if not txt.strip():
            return jsonify({"error": "missing text"}), 400

        generator = stream_tts_from_openai(txt)
        return Response(
            generator,
            mimetype="audio/mpeg",
            direct_passthrough=True,
        )

    except Exception as e:
        current_app.logger.exception(f"TTS error: {e}")
        return jsonify({"error": "Internal server error"}), 500
