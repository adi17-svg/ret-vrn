
# from flask import Blueprint, request, jsonify, Response, current_app
# import json
# import os
# import traceback
# from datetime import datetime
# from collections import defaultdict
# import requests
# import time
# from urllib.parse import quote_plus

# from tasks import generate_daily_task, save_completed_task, get_user_tasks
# from rewards import (
#     get_user_progress,
#     save_user_progress,
#     update_streak,
#     check_streak_rewards,
#     check_message_rewards,
# )
# from spiral_dynamics import (
#     detect_intent,
#     classify_stage,
#     check_evolution,
#     generate_reflective_question,
#     generate_gamified_prompt,
#     client,
#     build_mission_feedback_line,
# )
# from firebase_utils import db, save_conversation_message, get_recent_conversation
# from notifications import send_welcome_notification
# from tts import stream_tts_from_openai  # OpenAI TTS streamer

# bp = Blueprint("main", __name__)  # ✅ yahan __name__ hi use karna hai

# AUDIO_FOLDER = "audios"
# os.makedirs(AUDIO_FOLDER, exist_ok=True)

# # How many last messages to include as context (adjust as needed)
# HISTORY_LIMIT = 6

# XP_REWARDS = {
#     "level_up": 10,
#     "daily_streak_3": 15,
#     "daily_streak_7": 30,
#     "daily_streak_14": 50,
#     "daily_streak_30": 100,
#     "message_streak": 20,
# }

# BADGES = {
#     "level_up": "🌱 Level Up",
#     "daily_streak_3": "🔥 3-Day Streak",
#     "daily_streak_7": "🌟 Weekly Explorer",
#     "daily_streak_14": "🌙 Fortnight Champion",
#     "daily_streak_30": "🌕 Monthly Master",
#     "message_streak": "💬 Chatterbox",
# }

# # ✅ New mission milestone rewards
# MISSION_REWARDS = {
#     1: {"xp": 20, "badge": "🎯 First Mission"},
#     5: {"xp": 50, "badge": "🏅 Mission Explorer"},
#     10: {"xp": 100, "badge": "🚀 Mission Master"},
# }

# # ======================================================
# # RESPONSE TYPE DECIDER (Wysa-style logic)
# # ======================================================

# def decide_response_type(mood: str, intent: str) -> str:
#     """
#     Decides HOW to respond, not WHAT to say
#     """
#     if intent == "chat":
#         return "listen"

#     if mood in ["sad", "anxious", "overwhelmed", "tired", "stressed"]:
#         return "validate"

#     if mood in ["confused", "stuck", "uncertain"]:
#         return "reflect"

#     return "act"

# def process_reflection_core(
#     entry: str,
#     user_id: str | None,
#     last_stage: str = "",
#     reply_to: str = "",
# ):
#     """
#     FINAL STABLE VERSION

#     Returns (for frontend):
#     - mode: chat | spiral
#     - response: assistant text
#     - stage
#     - evolution (only if level increased)
#     - question (Mind Mirror)
#     - gamified (Mission)
#     - growth (mission text alias)
#     """

#     # --------------------------------------------------
#     # 1️⃣ SUPPORT FOCUS (soft bias only)
#     # --------------------------------------------------
#     support_focus = []
#     if user_id:
#         try:
#             doc = db.collection("users").document(user_id).get()
#             if doc.exists:
#                 support_focus = doc.to_dict().get("support_focus", [])
#         except Exception:
#             pass

#     # --------------------------------------------------
#     # 2️⃣ INTENT + SPIRAL CLASSIFICATION
#     # --------------------------------------------------
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

#     # --------------------------------------------------
#     # 3️⃣ RESPONSE TYPE (Wysa-style)
#     # --------------------------------------------------
#     response_type = decide_response_type(mood, intent)

#     # --------------------------------------------------
#     # 4️⃣ SPIRAL MODE ON / OFF
#     # --------------------------------------------------
#     spiral_active = bool(stage)

#     # very short / casual text → no spiral
#     if len(entry.split()) < 4:
#         spiral_active = False

#     # --------------------------------------------------
#     # 5️⃣ CONTEXT (PAST CHAT)
#     # --------------------------------------------------
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

#     # --------------------------------------------------
#     # 6️⃣ MIND MIRROR + MISSION
#     # --------------------------------------------------
#     question = ""
#     gamified = {}

#     if spiral_active:
#         try:
#             question = generate_reflective_question(entry, reply_to) or ""
#         except Exception:
#             question = ""

#         try:
#             gamified = generate_gamified_prompt(stage, entry) or {}
#         except Exception:
#             gamified = {}

#     # --------------------------------------------------
#     # 7️⃣ EVOLUTION CHECK (LEVEL UP)
#     # --------------------------------------------------
#     evolution_msg = None
#     if spiral_active and last_stage:
#         evolution_msg = check_evolution(
#             last_stage,
#             {
#                 "stage": stage,
#                 "confidence": confidence,
#             },
#         )

#     # --------------------------------------------------
#     # 8️⃣ SYSTEM PROMPT (LLM = language only)
#     # --------------------------------------------------
#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response style: {response_type}\n\n"
#         "Rules:\n"
#         "- validate → acknowledge feelings\n"
#         "- listen → stay present\n"
#         "- reflect → mirror insight\n"
#         "- act → suggest 1 gentle action\n\n"
#         f"User support focus (soft bias): {', '.join(support_focus) or 'none'}\n"
#         "Never mention it explicitly.\n"
#     )

#     if spiral_active:
#         system_prompt += (
#             "\nIntegrate naturally:\n"
#             f"Mind Mirror: {question}\n"
#             f"Mission: {gamified.get('gamified_prompt', '')}\n"
#         )

#     # --------------------------------------------------
#     # 9️⃣ GPT CALL
#     # --------------------------------------------------
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

#     # --------------------------------------------------
#     # 🔟 SAVE CONVERSATION
#     # --------------------------------------------------
#     if user_id:
#         try:
#             save_conversation_message(user_id, "user", entry)
#             save_conversation_message(user_id, "assistant", ai_text)
#         except Exception:
#             pass

#     # --------------------------------------------------
#     # 🔚 FINAL RESPONSE (FRONTEND CONTRACT)
#     # --------------------------------------------------
#     if not spiral_active:
#         return {
#             "mode": "chat",
#             "response": ai_text,
#         }

#     return {
#         "mode": "spiral",
#         "response": ai_text,

#         # 🌀 Spiral identity
#         "stage": stage,

#         # 🌱 Level-up message (optional)
#         "evolution": evolution_msg or "",

#         # 🧠 Mind Mirror
#         "question": question,

#         # 🎯 Mission
#         "gamified": gamified,
#         "growth": gamified.get("gamified_prompt", ""),

#         # 🏆 Safe defaults for UI
#         "badges_earned": [],
#     }


# @bp.route('/')
# def home():
#     return "Backend is running"


# @bp.route('/daily_task', methods=['GET'])
# def daily_task():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400
#     try:
#         task = generate_daily_task()
#         with open("completed_tasks.json") as f:
#             completed = json.load(f)
#         user_done = any(
#             t for t in completed if t.get("user_id") == user_id and t.get("date") == task.get("date") and t.get("completed")
#         )
#         task["user_done"] = user_done
#         return jsonify(task)
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to fetch daily task"}), 500


# @bp.route('/complete_task', methods=['POST'])
# def complete_task():
#     data = request.json
#     user_id = data.get("user_id")
#     task_id = data.get("task_id")
#     if not user_id or not task_id:
#         return jsonify({"error": "Missing user_id or task_id"}), 400
#     try:
#         with open("daily_tasks.json") as f:
#             tasks = json.load(f)
#         task_to_complete = next((t for t in tasks if str(t.get("timestamp")) == task_id and t.get("user_id") == user_id), None)
#         if not task_to_complete:
#             return jsonify({"error": "Task not found"}), 404
#         task_to_complete["completed"] = True
#         task_to_complete["completion_timestamp"] = datetime.utcnow().isoformat()
#         with open("daily_tasks.json", "w") as f:
#             json.dump(tasks, f, indent=2)
#         save_completed_task(user_id, task_to_complete)
#         return jsonify({"message": "Task marked completed"})
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to complete task"}), 500


# @bp.route('/task_history', methods=['GET'])
# def task_history():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400
#     try:
#         tasks = get_user_tasks(user_id, "completed_tasks.json")
#         return jsonify(tasks)
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to fetch task history"}), 500


# @bp.route('/user_progress', methods=['GET'])
# def user_progress():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400
#     try:
#         progress = get_user_progress(user_id)
#         return jsonify(progress)
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to fetch user progress"}), 500

# @bp.route("/merged", methods=["POST"])
# def merged():
#     data = request.json
#     entry = (data.get("text") or "").strip()

#     if not entry:
#         return jsonify({"error": "Missing text"}), 400

#     result = process_reflection_core(
#         entry=entry,
#         user_id=data.get("user_id"),
#         last_stage=data.get("last_stage", ""),
#         reply_to=data.get("reply_to", ""),
#     )

#     # 🔊 TTS
#     audio_url = f"{request.url_root.rstrip('/')}/speak-stream?text={quote_plus(result['response'])}"

#     result["audiourl"] = audio_url
#     return jsonify(result)

# @bp.route("/reflect_transcription", methods=["POST"])
# def reflect_transcription():
#     if "audio" not in request.files:
#         return jsonify({"error": "Missing audio"}), 400

#     user_id = request.form.get("user_id")
#     audio_file = request.files["audio"]

#     path = f"audios/{int(time.time())}.wav"
#     audio_file.save(path)

#     with open(path, "rb") as f:
#         transcript = client.audio.transcriptions.create(
#             model="gpt-4o-transcribe",
#             file=f,
#         )

#     text = (transcript.text or "").strip()

#     result = process_reflection_core(
#         entry=text,
#         user_id=user_id,
#     )

#     audio_url = f"{request.url_root.rstrip('/')}/speak-stream?text={quote_plus(result['response'])}"

#     result["audiourl"] = audio_url
#     result["transcription"] = text

#     return jsonify(result)

# # new endpoint for audio stream
# @bp.route("/speak-stream", methods=["GET", "POST"])
# def speak_stream():
#     """
#     Streams OpenAI TTS audio as MP3.
#     Koi file save nahi hoti, sirf generator se bytes stream hote hain.
#     """
#     try:
#         if request.method == "GET":
#             txt = request.args.get("text", "") or ""
#         else:
#             body = request.get_json(silent=True) or {}
#             txt = body.get("text", "") or ""

#         current_app.logger.info("==== SPEAK-STREAM ROUTE CALLED ====")
#         preview = txt[:120] + ("..." if len(txt) > 120 else "")
#         current_app.logger.info("speak-stream preview=%s len=%d", preview, len(txt))

#         if not txt.strip():
#             return jsonify({"error": "missing text"}), 400

#         # OpenAI TTS generator se stream karo (tts.py se)
#         generator = stream_tts_from_openai(txt)

#         return Response(generator, mimetype="audio/mpeg", direct_passthrough=True)

#     except Exception as e:
#         current_app.logger.exception(f"Error in speak-stream endpoint: {e}")
#         return jsonify({"error": "Internal server error"}), 500
    
# @bp.route('/finalize_stage', methods=['POST'])
# def finalize_stage():
#     try:
#         data = request.json
#         speaker_id = data.get("speaker_id")
#         speaker_stages = data.get("speaker_stages", {})
#         last_stage = data.get("last_stage", "")
#         reply_to = data.get("reply_to", "")
#         user_id = data.get("user_id")

#         if speaker_id not in speaker_stages:
#             return jsonify({"error": "Speaker not found"}), 400

#         speaker_info = speaker_stages[speaker_id]
#         current_stage = speaker_info.get("stage", "Unknown")
#         text = speaker_info.get("text", "")
#         evolution_msg = check_evolution(last_stage, {"stage": current_stage})

#         xp_gain = 0
#         badges = []
#         if user_id and evolution_msg:
#             progress = get_user_progress(user_id)
#             progress["xp"] += XP_REWARDS.get("level_up", 10)
#             if "level_up" not in progress.get("badges", []):
#                 progress["badges"].append("level_up")
#                 badges.append("🌱 Level Up")
#             save_user_progress(user_id, progress)
#             xp_gain = XP_REWARDS.get("level_up", 10)

#         # gamified = generate_gamified_prompt(current_stage, text, evolution=bool(evolution_msg))
#         gamified = generate_gamified_prompt(current_stage, text, evolution=bool(evolution_msg))
#         question = generate_reflective_question(text, reply_to)

#         # 🔊 Finalized stage ke liye TTS text
#         tts_parts = []
#         if current_stage:
#             tts_parts.append(f"Stage {current_stage}.")
#         if evolution_msg:
#             tts_parts.append(evolution_msg)
#         if question:
#             tts_parts.append(f"Mind Mirror question: {question}")
#         if gamified:
#             gq = gamified.get("gamified_question") or ""
#             gp = gamified.get("gamified_prompt") or ""
#             if gq:
#                 tts_parts.append(gq)
#             if gp:
#                 tts_parts.append(gp)

#         tts_text = " ".join(p for p in tts_parts if p)
#         base_url = request.url_root.rstrip("/")
#         audio_url = (
#             f"{base_url}/speak-stream?text={quote_plus(tts_text)}"
#             if tts_text else None
#         )
#         question = generate_reflective_question(text, reply_to)

#         return jsonify({
#             "stage": current_stage,
#             "question": question,
#             "evolution": evolution_msg,
#             "gamified": gamified,
#             "xp_gain": xp_gain,
#             "badges": badges,
#             "audiourl": audio_url,
#         })
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to finalize stage"}), 500
    
# @bp.route("/set_support_focus", methods=["POST"])
# def set_support_focus():
#     try:
#         data = request.get_json()
#         user_id = data.get("user_id")
#         support_focus = data.get("support_focus")

#         if not user_id:
#             return jsonify({"error": "Missing user_id"}), 400

#         if not support_focus:
#             # user skipped → do nothing
#             return jsonify({"status": "skipped"}), 200

#         # Normalize to list
#         if isinstance(support_focus, str):
#             support_focus = [support_focus]

#         # 🔹 STORE IN SAME USER DOCUMENT (NO NEW COLLECTION)
#         db.collection("users").document(user_id).set(
#             {
#                 "support_focus": support_focus,
#                 "support_focus_set_at": datetime.utcnow(),
#             },
#             merge=True
#         )

#         return jsonify({"status": "saved", "support_focus": support_focus})

#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to store support focus"}), 500

# from flask import Blueprint, request, jsonify, Response, current_app
# import json
# import os
# import traceback
# from datetime import datetime
# import time
# from urllib.parse import quote_plus

# from tasks import generate_daily_task, save_completed_task, get_user_tasks
# from rewards import (
#     get_user_progress,
#     save_user_progress,
#     update_streak,
#     check_streak_rewards,
#     check_message_rewards,
# )
# from spiral_dynamics import (
#     detect_intent,
#     classify_stage,
#     check_evolution,
#     generate_reflective_question,
#     generate_gamified_prompt,
#     client,
# )
# from firebase_utils import db, save_conversation_message, get_recent_conversation
# from tts import stream_tts_from_openai

# bp = Blueprint("main", __name__)

# HISTORY_LIMIT = 6
# AUDIO_FOLDER = "audios"
# os.makedirs(AUDIO_FOLDER, exist_ok=True)

# DYSREGULATED_MOODS = [
#     "angry", "sad", "anxious", "overwhelmed", "confused", "stressed", "tired"
# ]

# # ======================================================
# # RESPONSE TYPE DECIDER (Wysa-style)
# # ======================================================
# def decide_response_type(mood: str, intent: str) -> str:
#     if intent == "chat":
#         return "listen"
#     if mood in ["sad", "anxious", "overwhelmed", "tired", "stressed"]:
#         return "validate"
#     if mood in ["confused", "stuck", "uncertain"]:
#         return "reflect"
#     return "act"


# # ======================================================
# # CORE BRAIN
# # ======================================================
# def process_reflection_core(
#     entry: str,
#     user_id: str | None,
#     last_stage: str = "",
#     reply_to: str = "",
# ):
#     """
#     Unified response format (NO chat / spiral mode)

#     Returns:
#     {
#       message: { text, tone },
#       reflection: { mind_mirror },
#       action: { mission, requires_permission },
#       pattern: { stage, evolution }
#     }
#     """

#     # -----------------------------
#     # 1️⃣ Support focus (soft bias)
#     # -----------------------------
#     support_focus = []
#     if user_id:
#         try:
#             doc = db.collection("users").document(user_id).get()
#             if doc.exists:
#                 support_focus = doc.to_dict().get("support_focus", [])
#         except Exception:
#             pass

#     # -----------------------------
#     # 2️⃣ Intent + Stage detection
#     # -----------------------------
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

#     # -----------------------------
#     # 3️⃣ Response style
#     # -----------------------------
#     response_type = decide_response_type(mood, intent)

#     # -----------------------------
#     # 4️⃣ Spiral allowed or not
#     # -----------------------------
#     spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
#     if len(entry.split()) < 4:
#         spiral_active = False

#     # -----------------------------
#     # 5️⃣ Context (memory)
#     # -----------------------------
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

#     # -----------------------------
#     # 6️⃣ Mind Mirror vs Mission
#     # -----------------------------
#     question = None
#     mission = None

#     # 🧠 Mind Mirror → awareness (no action)
#     if response_type in ["validate", "reflect"]:
#         try:
#             question = generate_reflective_question(entry, reply_to)
#         except Exception:
#             question = None

#     # 🎯 Mission → only if user is ready
#     if response_type == "act" and spiral_active:
#         try:
#             gamified = generate_gamified_prompt(stage, entry)
#             mission = gamified.get("gamified_prompt")
#         except Exception:
#             mission = None

#     # -----------------------------
#     # 7️⃣ Evolution (growth only)
#     # -----------------------------
#     evolution_msg = None
#     if spiral_active and last_stage:
#         evolution_msg = check_evolution(
#             last_stage,
#             {"stage": stage, "confidence": confidence},
#         )

#     # -----------------------------
#     # 8️⃣ System prompt (language only)
#     # -----------------------------
#     system_prompt = (
#         "You are a warm, grounded companion in the RETVRN app.\n\n"
#         f"Response tone: {response_type}\n\n"
#         "Rules:\n"
#         "- Validate emotions first\n"
#         "- Slow the pace\n"
#         "- Keep sentences short\n"
#         "- Never force action\n"
#         "- Offer choice gently\n\n"
#         f"User support focus (do NOT mention): {', '.join(support_focus) or 'none'}\n"
#     )

#     if question:
#         system_prompt += f"\nAsk gently (Mind Mirror): {question}\n"

#     if mission:
#         system_prompt += (
#             "\nOffer this only if the user agrees:\n"
#             f"{mission}\n"
#         )

#     # -----------------------------
#     # 9️⃣ GPT Call
#     # -----------------------------
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

#     # -----------------------------
#     # 🔟 Save conversation
#     # -----------------------------
#     if user_id:
#         try:
#             save_conversation_message(user_id, "user", entry)
#             save_conversation_message(user_id, "assistant", ai_text)
#         except Exception:
#             pass

#     # -----------------------------
#     # ✅ FINAL UNIFIED RESPONSE
#     # -----------------------------
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


# # ======================================================
# # ROUTES
# # ======================================================
# @bp.route("/")
# def home():
#     return "Backend is running"


# @bp.route("/merged", methods=["POST"])
# def merged():
#     data = request.json
#     entry = (data.get("text") or "").strip()

#     if not entry:
#         return jsonify({"error": "Missing text"}), 400

#     result = process_reflection_core(
#         entry=entry,
#         user_id=data.get("user_id"),
#         last_stage=data.get("last_stage", ""),
#         reply_to=data.get("reply_to", ""),
#     )

#     audio_url = f"{request.url_root.rstrip('/')}/speak-stream?text={quote_plus(result['message']['text'])}"
#     result["audiourl"] = audio_url

#     return jsonify(result)


# @bp.route("/reflect_transcription", methods=["POST"])
# def reflect_transcription():
#     if "audio" not in request.files:
#         return jsonify({"error": "Missing audio"}), 400

#     user_id = request.form.get("user_id")
#     audio_file = request.files["audio"]

#     path = f"audios/{int(time.time())}.wav"
#     audio_file.save(path)

#     with open(path, "rb") as f:
#         transcript = client.audio.transcriptions.create(
#             model="gpt-4o-transcribe",
#             file=f,
#         )

#     text = (transcript.text or "").strip()

#     result = process_reflection_core(
#         entry=text,
#         user_id=user_id,
#     )

#     audio_url = f"{request.url_root.rstrip('/')}/speak-stream?text={quote_plus(result['message']['text'])}"
#     result["audiourl"] = audio_url
#     result["transcription"] = text

#     return jsonify(result)


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
#         return Response(generator, mimetype="audio/mpeg", direct_passthrough=True)

#     except Exception as e:
#         current_app.logger.exception(f"TTS error: {e}")
# #         return jsonify({"error": "Internal server error"}), 500
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

def process_reflection_core(
    entry: str,
    user_id: str | None,
    last_stage: str = "",
    reply_to: str = "",
    tool_id: str | None = None,   # ✅ NEW (OPTIONAL)
):
    """
    THE ONLY PLACE WHERE THINKING HAPPENS
    """

    # 1️⃣ User support focus (soft bias only)
    support_focus = []
    if user_id:
        try:
            doc = db.collection("users").document(user_id).get()
            if doc.exists:
                support_focus = doc.to_dict().get("support_focus", [])
        except Exception:
            pass

    # 2️⃣ Intent + Spiral classification (INTERNAL)
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

    # 3️⃣ Decide response tone (Wysa rule)
    response_type = decide_response_type(mood, intent)

    if reply_to == "gratitude_prompt":
        response_type = "listen"

    # 4️⃣ Spiral guardrail
    spiral_active = bool(stage) and mood not in DYSREGULATED_MOODS
    if len(entry.split()) < 4:
        spiral_active = False

    # 🚫 TOOL MODE → spiral / growth OFF
    if tool_id:
        spiral_active = False
        response_type = "listen"   # ✅ ADD THIS LINE

    # 🔄 Spiral tracking (ONLY for main chat)
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

    # 6️⃣ Mind mirror vs mission
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
    
      
    # 🚨 TOOL MODE OVERRIDE — RUN TOOL INSTEAD OF GPT
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

    # 9️⃣ Save memory (chat history only, safe for tools too)
    if user_id:
        try:
            save_conversation_message(user_id, "user", entry)
            save_conversation_message(user_id, "assistant", ai_text)
        except Exception:
            pass

    # ✅ FINAL unified response
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
@bp.route("/merged", methods=["POST"])
def merged():
    data = request.json or {}

    entry = (data.get("text") or "").strip()

    user_id = data.get("user_id")
    last_stage = data.get("last_stage", "")
    reply_to = data.get("reply_to", "")

    # 🔹 TOOL CONTEXT
    tool_id = data.get("tool_id")          # None for main chat
    tool_step = data.get("tool_step")      # None on first step

    # =========================
    # 🧠 TOOL MODE
    # =========================
    if tool_id:
        tool_response = run_tool(
            tool_id=tool_id,
            step=tool_step,
            user_text=entry or None,   # 👈 allow empty
        )

        if not tool_response:
            return jsonify({"error": "Invalid tool"}), 400

        # save conversation (optional, safe)
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

    # =========================
    # 💬 MAIN CHAT (UNCHANGED)
    # =========================
    if not entry:
        return jsonify({"error": "Missing text"}), 400

    result = process_reflection_core(
        entry=entry,
        user_id=user_id,
        last_stage=last_stage,
        reply_to=reply_to,
        tool_id=None,
    )

    audio_url = (
        f"{request.url_root.rstrip('/')}speak-stream"
        f"?text={quote_plus(result['message']['text'])}"
    )
    result["audiourl"] = audio_url

    return jsonify(result)

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
