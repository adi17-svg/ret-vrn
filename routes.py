
# from flask import Blueprint, request, jsonify
# import json
# import os
# import traceback
# from datetime import datetime
# from collections import defaultdict
# import requests

# # Import your project modules - adjust import paths as necessary
# from tasks import generate_daily_task, save_completed_task, get_user_tasks
# from rewards import get_user_progress, save_user_progress, update_streak, check_streak_rewards, check_message_rewards
# from spiral_dynamics import detect_intent, classify_stage, check_evolution, generate_reflective_question, generate_gamified_prompt
# from firebase_utils import db
# from notifications import send_welcome_notification
# # from openai import OpenAI  # Your AI client instance configured elsewhere
# from spiral_dynamics import client  # Your OpenAI client instance

# bp = Blueprint('main', __name__)

# AUDIO_FOLDER = "audios"
# os.makedirs(AUDIO_FOLDER, exist_ok=True)

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


# @bp.route('/merged', methods=['POST'])
# def merged():
#     try:
#         data = request.json
#         entry = data.get("text", "").strip()
#         last_stage = data.get("last_stage", "").strip()
#         reply_to = data.get("reply_to", "").strip()
#         user_id = data.get("user_id")
#         if not entry:
#             return jsonify({"error": "Missing entry"}), 400

#         streak = 0
#         rewards = []
#         message_rewards = []
#         missions_completed = 0
#         new_mission_reward = None

#         if user_id:
#             streak = update_streak(user_id)
#             rewards = check_streak_rewards(user_id, streak)
#             message_rewards = check_message_rewards(user_id)

#         # ✅ Mission tracking if replying
#         if reply_to and user_id:
#             try:
#                 with open("daily_tasks.json") as f:
#                     tasks = json.load(f)
#                 task_to_complete = next(
#                     (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
#                     None
#                 )
#                 if task_to_complete:
#                     save_completed_task(user_id, task_to_complete)

#                     # Increment missions completed
#                     progress = get_user_progress(user_id)
#                     progress["missions_completed"] = progress.get("missions_completed", 0) + 1
#                     missions_completed = progress["missions_completed"]

#                     # Check mission milestone rewards
#                     if missions_completed in MISSION_REWARDS:
#                         reward = MISSION_REWARDS[missions_completed]
#                         progress["xp"] += reward["xp"]
#                         if reward["badge"] not in progress.get("badges", []):
#                             progress["badges"].append(reward["badge"])
#                         new_mission_reward = reward
#                     save_user_progress(user_id, progress)
#             except Exception as e:
#                 print("⚠ Error marking growth prompt complete:", e)

#         # Normal reflection/chat logic
#         intent = detect_intent(entry)
#         if intent == "chat":
#             prompt_msg = entry
#             if reply_to:
#                 prompt_msg = f"Previous: {reply_to}\nUser: {entry}"
#             ai_resp = client.chat.completions.create(
#                 model='gpt-4.1',
#                 messages=[{"role": "user", "content": f"Be a kind friend and casually respond to:\n{prompt_msg}"}],
#                 temperature=0.7,
#             ).choices[0].message.content.strip()
#             return jsonify({
#                 "mode": "chat",
#                 "response": ai_resp,
#                 "streak": streak,
#                 "rewards": rewards,
#                 "message_rewards": message_rewards,
#                 "missions_completed": missions_completed,
#                 "new_mission_reward": new_mission_reward,
#             })

#         classification = classify_stage(entry)
#         stage = classification.get("stage")
#         evolution_msg = check_evolution(last_stage, classification)

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

#         gamified = generate_gamified_prompt(stage or last_stage, entry, evolution=bool(evolution_msg))
#         question = generate_reflective_question(entry, reply_to)

#         response = {
#             "mode": "spiral",
#             "stage": stage,
#             "evolution": evolution_msg,
#             "xp_gain": xp_gain,
#             "badges": badges,
#             "question": question,
#             "gamified": gamified,
#             "confidence": classification.get("confidence"),
#             "reason": classification.get("reason"),
#             "streak": streak,
#             "rewards": rewards,
#             "message_rewards": message_rewards,
#             "missions_completed": missions_completed,
#             "new_mission_reward": new_mission_reward,
#         }
#         if classification.get("confidence", 1) < 0.7 and classification.get("secondary"):
#             response["note"] = f"Also detected: {classification['secondary']}"
#         return jsonify(response)

#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to process reflection"}), 500


# @bp.route('/reflect_transcription', methods=['POST'])
# def reflect_transcription():
#     try:
#         if 'audio' not in request.files:
#             return jsonify({"error": "Missing audio file"}), 400
#         reply_to = request.form.get("reply_to", "")
#         last_stage = request.form.get("last_stage", "")
#         user_id = request.form.get("user_id", "")
#         audio_file = request.files['audio']

#         streak = 0
#         rewards = []
#         message_rewards = []
#         missions_completed = 0
#         new_mission_reward = None

#         if user_id:
#             streak = update_streak(user_id)
#             rewards = check_streak_rewards(user_id, streak)
#             message_rewards = check_message_rewards(user_id)

#         # ✅ Mission tracking if replying (audio)
#         if reply_to and user_id:
#             try:
#                 with open("daily_tasks.json") as f:
#                     tasks = json.load(f)
#                 task_to_complete = next(
#                     (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
#                     None
#                 )
#                 if task_to_complete:
#                     save_completed_task(user_id, task_to_complete)

#                     # Increment missions completed
#                     progress = get_user_progress(user_id)
#                     progress["missions_completed"] = progress.get("missions_completed", 0) + 1
#                     missions_completed = progress["missions_completed"]

#                     # Check mission milestone rewards
#                     if missions_completed in MISSION_REWARDS:
#                         reward = MISSION_REWARDS[missions_completed]
#                         progress["xp"] += reward["xp"]
#                         if reward["badge"] not in progress.get("badges", []):
#                             progress["badges"].append(reward["badge"])
#                         new_mission_reward = reward
#                     save_user_progress(user_id, progress)
#             except Exception as e:
#                 print("⚠ Error marking growth prompt complete (audio):", e)

#         filename = f"{user_id or 'anon'}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.wav"
#         os.makedirs("audios", exist_ok=True)
#         path = os.path.join("audios", filename)
#         audio_file.save(path)

#         upload_resp = requests.post(
#             "https://api.assemblyai.com/v2/upload",
#             headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY"), "content-type": "application/octet-stream"},
#             data=open(path, "rb")
#         )
#         audio_url = upload_resp.json().get("upload_url")
#         transcript_post = requests.post(
#             "https://api.assemblyai.com/v2/transcript",
#             headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
#             json={"audio_url": audio_url, "speaker_labels": True}
#         )
#         transcript_id = transcript_post.json().get("id")

#         while True:
#             poll_resp = requests.get(
#                 f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
#                 headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
#             )
#             poll_data = poll_resp.json()
#             if poll_data.get("status") in ("completed", "error"):
#                 break

#         if poll_data.get("status") == "error":
#             return jsonify({"error": "Transcription failed"}), 500

#         transcript_text = poll_data.get("text", "")
#         utterances = poll_data.get("utterances", [])
#         dialogue = "\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in utterances)

#         intent = detect_intent(transcript_text)
#         # try:
#         #     intent = detect_intent(transcript_text)
#         # except openai.InternalServerError as e:
#         #     app.logger.error(f"API error: {e}")
#         #     return jsonify(error="Upstream AI service error, please try later"), 503
#         if intent == "chat":
#             ai_resp = client.chat.completions.create(
#                 model='gpt-4.1',
#                 messages=[{"role": "user", "content": f"Carefully respond to:\n{dialogue}"}],
#                 temperature=0.7,
#             ).choices[0].message.content.strip()
#             return jsonify({
#                 "mode": "chat",
#                 "response": ai_resp,
#                 "transcription": dialogue,
#                 "diarized": True,
#                 "streak": streak,
#                 "rewards": rewards,
#                 "message_rewards": message_rewards,
#                 "missions_completed": missions_completed,
#                 "new_mission_reward": new_mission_reward,
#             })

#         speaker_texts = defaultdict(str)
#         for u in utterances:
#             speaker_name = f"Speaker {u['speaker']}"
#             speaker_texts[speaker_name] += u["text"] + " "

#         speaker_stages = {}
#         for speaker_name, text in speaker_texts.items():
#             try:
#                 stage_info = classify_stage(text.strip())
#                 speaker_stages[speaker_name] = {"stage": stage_info["stage"], "text": text.strip()}
#             except Exception as e:
#                 speaker_stages[speaker_name] = {"stage": "Unknown", "text": text.strip(), "error": str(e)}

#         return jsonify({
#             "mode": "spiral",
#             "transcription": dialogue,
#             "speaker_stages": speaker_stages,
#             "diarized": True,
#             "ask_speaker_pick": True,
#             "streak": streak,
#             "rewards": rewards,
#             "message_rewards": message_rewards,
#             "missions_completed": missions_completed,
#             "new_mission_reward": new_mission_reward,
#         })
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to process transcription"}), 500


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

#         gamified = generate_gamified_prompt(current_stage, text, evolution=bool(evolution_msg))
#         question = generate_reflective_question(text, reply_to)

#         return jsonify({
#             "stage": current_stage,
#             "question": question,
#             "evolution": evolution_msg,
#             "gamified": gamified,
#             "xp_gain": xp_gain,
#             "badges": badges,
#         })   
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to finalize stage"}), 500
# routes.py
# from flask import Blueprint, request, jsonify
# import json
# import os
# import traceback
# from datetime import datetime
# from collections import defaultdict
# import requests

# # Import your project modules - adjust import paths as necessary
# from tasks import generate_daily_task, save_completed_task, get_user_tasks
# from rewards import get_user_progress, save_user_progress, update_streak, check_streak_rewards, check_message_rewards
# from spiral_dynamics import detect_intent, classify_stage, check_evolution, generate_reflective_question, generate_gamified_prompt
# from firebase_utils import db, save_conversation_message, get_recent_conversation
# from notifications import send_welcome_notification
# # from openai import OpenAI  # Your AI client instance configured elsewhere
# from spiral_dynamics import client  # Your OpenAI client instance
# # add near other imports
# from flask import Response, request, jsonify
# from tts import stream_tts_from_openai
# from flask import current_app


# bp = Blueprint('main', __name__)


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

# @bp.route('/merged', methods=['POST'])
# def merged():
#     """
#     Backend-only: ensure model references 'Mind Mirror' and 'Mission' (or both).
#     Uses existing helpers. Also performs a quiet mood/stage detection on each user message
#     and stores it in user progress (invisible to the user).
#     """
#     try:
#         data = request.json
#         entry = data.get("text", "").strip()
#         last_stage = data.get("last_stage", "").strip()
#         reply_to = data.get("reply_to", "").strip()
#         user_id = data.get("user_id")
#         if not entry:
#             return jsonify({"error": "Missing entry"}), 400

#         streak = 0
#         rewards = []
#         message_rewards = []
#         missions_completed = 0
#         new_mission_reward = None

#         if user_id:
#             streak = update_streak(user_id)
#             rewards = check_streak_rewards(user_id, streak)
#             message_rewards = check_message_rewards(user_id)

#         # Mission completion if replying to a task
#         if reply_to and user_id:
#             try:
#                 with open("daily_tasks.json") as f:
#                     tasks = json.load(f)
#                 task_to_complete = next(
#                     (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
#                     None
#                 )
#                 if task_to_complete:
#                     save_completed_task(user_id, task_to_complete)
#                     progress = get_user_progress(user_id)
#                     progress["missions_completed"] = progress.get("missions_completed", 0) + 1
#                     missions_completed = progress["missions_completed"]
#                     if missions_completed in MISSION_REWARDS:
#                         reward = MISSION_REWARDS[missions_completed]
#                         progress["xp"] += reward["xp"]
#                         if reward["badge"] not in progress.get("badges", []):
#                             progress["badges"].append(reward["badge"])
#                         new_mission_reward = reward
#                     save_user_progress(user_id, progress)
#             except Exception as e:
#                 print("⚠ Error marking growth prompt complete:", e)

#         # Save raw incoming user entry as memory
#         if user_id:
#             try:
#                 save_conversation_message(user_id, "user", entry)
#             except Exception as e:
#                 print("⚠ Warning: could not save incoming message:", e)

#         # --- Hidden: detect mood / stage from user message (backend-only, not shown to user) ---
#         if user_id:
#             try:
#                 # Small context to help classifier (fetch last few msgs quietly)
#                 try:
#                     _recent_small = get_recent_conversation(user_id, limit=3)
#                     _context_text = "\n".join([f"{m['role']}: {m['content']}" for m in _recent_small])
#                 except Exception:
#                     _context_text = ""

#                 # Run the classifier quietly (it should return stage, confidence, maybe mood)
#                 try:
#                     _classification_quiet = classify_stage(entry, context=_context_text)
#                 except TypeError:
#                     _classification_quiet = classify_stage(entry)

#                 # Extract values we care about
#                 detected_stage = _classification_quiet.get("stage")
#                 detected_confidence = float(_classification_quiet.get("confidence", 0) or 0)
#                 detected_mood = _classification_quiet.get("mood") or _classification_quiet.get("emotion") or None

#                 # Persist detection quietly in user's progress/profile (no frontend exposure)
#                 try:
#                     progress = get_user_progress(user_id)
#                     progress["_last_detected_stage"] = detected_stage
#                     progress["_last_stage_confidence"] = detected_confidence
#                     progress["_last_detected_mood"] = detected_mood
#                     progress["_last_stage_ts"] = int(time.time() * 1000)
#                     save_user_progress(user_id, progress)
#                 except Exception as e:
#                     print("⚠ Could not save quiet stage/mood metadata:", e)

#             except Exception as e:
#                 print("⚠ Mood/stage detection failed (quiet):", e)

#         # Build context messages for OpenAI
#         messages_for_ai = []
#         # persona/system message first
#         # system_msg = {
#         #     "role": "system",
#         #     "content": "You are a kind, reflective Spiral Dynamics mentor and supportive chatbot for RETVRN. Keep replies concise and empathetic."
#         # }
#         system_msg = {
#     "role": "system",
#     "content": (
#         "You are a warm, natural, conversational companion for RETVRN who speaks like a supportive friend. "
#         "Be kind and reflective, but avoid formal or robotic phrasing — use contractions, short paragraphs, and "
#         "simple everyday language. If the user has just completed a mission, briefly celebrate (1–2 lines), "
#         "then follow with an open, friendly follow-up question to keep the chat going. Keep responses human, varied, "
#         "and gently encouraging while staying concise."
#     )
# }

#         messages_for_ai.append(system_msg)

#         # Helper: parse latest assistant message for Mind Mirror and Mission
#         def _get_latest_mindmirror_mission(uid):
#             try:
#                 recent = get_recent_conversation(uid, limit=12)  # look back a bit further for mission/mindmirror
#             except Exception:
#                 return None, None
#             # search newest -> oldest
#             for m in reversed(recent):
#                 if m.get("role") == "assistant" and m.get("content"):
#                     content = m["content"]
#                     mind = None
#                     mission = None
#                     for line in content.splitlines():
#                         ln = line.strip()
#                         if ln.lower().startswith("mind mirror:"):
#                             mind = ln.split(":", 1)[1].strip()
#                         elif ln.lower().startswith("mission:"):
#                             mission = ln.split(":", 1)[1].strip()
#                     if mind or mission:
#                         return mind, mission
#             return None, None

#         # If we have a user_id, fetch recent messages and append (oldest -> newest)
#         if user_id:
#             try:
#                 recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
#                 for m in recent:
#                     r = m.get("role", "user")
#                     if r not in ("user", "assistant", "system"):
#                         r = "user"
#                     messages_for_ai.append({"role": r, "content": m.get("content", "")})
#                 # explicit assistant snippet containing latest Mind Mirror / Mission (if any)
#                 mind_mirror_text, mission_text = _get_latest_mindmirror_mission(user_id)
#                 if mind_mirror_text or mission_text:
#                     explicit_snip = (
#                         f"Latest Mind Mirror: {mind_mirror_text or '—'}\n"
#                         f"Latest Mission: {mission_text or '—'}"
#                     )
#                     # Append as assistant role to ensure visibility (won't change UI)
#                     messages_for_ai.append({"role": "assistant", "content": explicit_snip})
#             except Exception as e:
#                 print("⚠ Could not fetch recent conversation:", e)

#         # Additional system instruction to nudge model to use Mind Mirror/Mission when present
#         # messages_for_ai.insert(1, {
#         #     "role": "system",
#         #     "content": (
#         #         "When answering, first check for any 'Latest Mind Mirror' and 'Latest Mission' in the conversation. "
#         #         "If present, briefly reference them and tailor suggestions to align with that Mind Mirror and/or Mission. "
#         #         "If neither is present, answer normally and empathetically."
#         #     )
#         # })
#         messages_for_ai.insert(1, {
#     "role": "system",
#     "content": (
#         "When answering, first check for any 'Latest Mind Mirror' and 'Latest Mission' in the conversation. "
#         "If present, briefly reference them so your reply feels connected to the user's recent reflection or task. "
#         "If the user has just completed the mission, celebrate briefly (a warm, casual line), then ask a friendly, "
#         "open-ended follow-up that invites more sharing (e.g., 'How did that feel?' or 'Anything surprising?'). "
#         "Always avoid sounding formal or repetitive — aim to sound like a compassionate human companion."
#     )
# })


#         # Append the current user message last
#         current_user_content = entry if not reply_to else f"Previous: {reply_to}\nUser: {entry}"
#         messages_for_ai.append({"role": "user", "content": current_user_content})

#         # Decide intent
#         intent = detect_intent(entry)

#         # ---------------------------
#         # Chat (casual) flow
#         # ---------------------------
#         if intent == "chat":
#             try:
#                 resp = client.chat.completions.create(
#                     model='gpt-4.1',
#                     messages=messages_for_ai,
#                     temperature=0.7,
#                 )
#                 ai_resp = resp.choices[0].message.content.strip()
#             except Exception as e:
#                 print("AI chat error, falling back:", e)
#                 try:
#                     ai_resp = client.chat.completions.create(
#                         model='gpt-4.1',
#                         messages=[{"role": "user", "content": f"Be a kind friend and casually respond to:\n{current_user_content}"}],
#                         temperature=0.7
#                     ).choices[0].message.content.strip()
#                 except Exception as e2:
#                     print("Fallback AI also failed:", e2)
#                     return jsonify({"error": "AI service unavailable"}), 503

#             # Save assistant response
#             if user_id:
#                 try:
#                     save_conversation_message(user_id, "assistant", ai_resp)
#                 except Exception as e:
#                     print("⚠ Could not save assistant reply:", e)

#             return jsonify({
#                 "mode": "chat",
#                 "response": ai_resp,
#                 "streak": streak,
#                 "rewards": rewards,
#                 "message_rewards": message_rewards,
#                 "missions_completed": missions_completed,
#                 "new_mission_reward": new_mission_reward,
#             })

#         # ---------------------------
#         # Spiral (reflection) flow
#         # ---------------------------
#         # Provide a small context string for classifier/question generator
#         context_text = ""
#         if user_id:
#             try:
#                 recent_small = get_recent_conversation(user_id, limit=3)
#                 context_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent_small])
#             except Exception:
#                 context_text = ""

#         # classify_stage may accept context
#         try:
#             classification = classify_stage(entry, context=context_text)
#         except TypeError:
#             classification = classify_stage(entry)

#         stage = classification.get("stage")
#         # prefer classification-provided mind mirror if available
#         mind_mirror_gen = classification.get("mind_mirror") or classification.get("mind_mirror_text") or None
#         evolution_msg = check_evolution(last_stage, classification)

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

#         # gamified prompt treated as Mission
#         gamified = generate_gamified_prompt(stage or last_stage, entry, evolution=bool(evolution_msg))

#         # generate_reflective_question - backcompat handled
#         try:
#             question = generate_reflective_question(entry, reply_to=reply_to or None, context=context_text)
#         except TypeError:
#             question = generate_reflective_question(entry, reply_to)

#         # Save assistant-generated question to conversation store
#         if user_id and question:
#             try:
#                 save_conversation_message(user_id, "assistant", question)
#             except Exception as e:
#                 print("⚠ Could not save assistant question:", e)

#         # --- Save a single structured assistant message containing Stage / Mind Mirror / Mission / Question
#         if user_id:
#             try:
#                 # Build parseable block; prefer generated mind mirror, fallback to latest saved one if present
#                 mm = mind_mirror_gen
#                 prev_mind = None
#                 prev_mission = None
#                 if not mm:
#                     # try to fetch existing latest Mind Mirror from previous assistant messages
#                     prev_mind, prev_mission = _get_latest_mindmirror_mission(user_id)
#                     if prev_mind:
#                         mm = prev_mind

#                 mission_text_block = gamified or (prev_mission if prev_mission else None)
#                 mission_lines = [
#                     f"Stage: {stage or last_stage}",
#                     f"Mind Mirror: {mm or '—'}",
#                     f"Mission: {mission_text_block or '—'}",
#                     f"Question: {question or '—'}"
#                 ]
#                 mission_block = "\n".join([ln for ln in mission_lines if ln.strip()])
#                 save_conversation_message(user_id, "assistant", mission_block)
#             except Exception as e:
#                 print("⚠ Could not save mission/mind-mirror block:", e)

#         response = {
#             "mode": "spiral",
#             "stage": stage,
#             "evolution": evolution_msg,
#             "xp_gain": xp_gain,
#             "badges": badges,
#             "question": question,
#             "gamified": gamified,
#             "confidence": classification.get("confidence"),
#             "reason": classification.get("reason"),
#             "streak": streak,
#             "rewards": rewards,
#             "message_rewards": message_rewards,
#             "missions_completed": missions_completed,
#             "new_mission_reward": new_mission_reward,
#         }
#         if classification.get("confidence", 1) < 0.7 and classification.get("secondary"):
#             response["note"] = f"Also detected: {classification['secondary']}"
#         return jsonify(response)

#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to process reflection"}), 500


# @bp.route('/reflect_transcription', methods=['POST'])
# def reflect_transcription():
#     try:
#         if 'audio' not in request.files:
#             return jsonify({"error": "Missing audio file"}), 400
#         reply_to = request.form.get("reply_to", "")
#         last_stage = request.form.get("last_stage", "")
#         user_id = request.form.get("user_id", "")
#         audio_file = request.files['audio']

#         streak = 0
#         rewards = []
#         message_rewards = []
#         missions_completed = 0
#         new_mission_reward = None

#         if user_id:
#             streak = update_streak(user_id)
#             rewards = check_streak_rewards(user_id, streak)
#             message_rewards = check_message_rewards(user_id)

#         # ✅ Mission tracking if replying (audio)
#         if reply_to and user_id:
#             try:
#                 with open("daily_tasks.json") as f:
#                     tasks = json.load(f)
#                 task_to_complete = next(
#                     (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
#                     None
#                 )
#                 if task_to_complete:
#                     save_completed_task(user_id, task_to_complete)

#                     # Increment missions completed
#                     progress = get_user_progress(user_id)
#                     progress["missions_completed"] = progress.get("missions_completed", 0) + 1
#                     missions_completed = progress["missions_completed"]

#                     # Check mission milestone rewards
#                     if missions_completed in MISSION_REWARDS:
#                         reward = MISSION_REWARDS[missions_completed]
#                         progress["xp"] += reward["xp"]
#                         if reward["badge"] not in progress.get("badges", []):
#                             progress["badges"].append(reward["badge"])
#                         new_mission_reward = reward
#                     save_user_progress(user_id, progress)
#             except Exception as e:
#                 print("⚠ Error marking growth prompt complete (audio):", e)

#         filename = f"{user_id or 'anon'}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.wav"
#         os.makedirs("audios", exist_ok=True)
#         path = os.path.join("audios", filename)
#         audio_file.save(path)

#         upload_resp = requests.post(
#             "https://api.assemblyai.com/v2/upload",
#             headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY"), "content-type": "application/octet-stream"},
#             data=open(path, "rb")
#         )
#         audio_url = upload_resp.json().get("upload_url")
#         transcript_post = requests.post(
#             "https://api.assemblyai.com/v2/transcript",
#             headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
#             json={"audio_url": audio_url, "speaker_labels": True}
#         )
#         transcript_id = transcript_post.json().get("id")

#         while True:
#             poll_resp = requests.get(
#                 f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
#                 headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
#             )
#             poll_data = poll_resp.json()
#             if poll_data.get("status") in ("completed", "error"):
#                 break

#         if poll_data.get("status") == "error":
#             return jsonify({"error": "Transcription failed"}), 500

#         transcript_text = poll_data.get("text", "")
#         utterances = poll_data.get("utterances", [])
#         dialogue = "\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in utterances)

#         intent = detect_intent(transcript_text)
#         if intent == "chat":
#             ai_resp = client.chat.completions.create(
#                 model='gpt-4.1',
#                 messages=[{"role": "user", "content": f"Carefully respond to:\n{dialogue}"}],
#                 temperature=0.7,
#             ).choices[0].message.content.strip()
#             return jsonify({
#                 "mode": "chat",
#                 "response": ai_resp,
#                 "transcription": dialogue,
#                 "diarized": True,
#                 "streak": streak,
#                 "rewards": rewards,
#                 "message_rewards": message_rewards,
#                 "missions_completed": missions_completed,
#                 "new_mission_reward": new_mission_reward,
#             })

#         speaker_texts = defaultdict(str)
#         for u in utterances:
#             speaker_name = f"Speaker {u['speaker']}"
#             speaker_texts[speaker_name] += u["text"] + " "

#         speaker_stages = {}
#         for speaker_name, text in speaker_texts.items():
#             try:
#                 stage_info = classify_stage(text.strip())
#                 speaker_stages[speaker_name] = {"stage": stage_info["stage"], "text": text.strip()}
#             except Exception as e:
#                 speaker_stages[speaker_name] = {"stage": "Unknown", "text": text.strip(), "error": str(e)}

#         return jsonify({
#             "mode": "spiral",
#             "transcription": dialogue,
#             "speaker_stages": speaker_stages,
#             "diarized": True,
#             "ask_speaker_pick": True,
#             "streak": streak,
#             "rewards": rewards,
#             "message_rewards": message_rewards,
#             "missions_completed": missions_completed,
#             "new_mission_reward": new_mission_reward,
#         })
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to process transcription"}), 500
# # new endpoint for audio stream
# # in routes.py (replace existing speak_stream route)

# # @bp.route("/speak-stream", methods=["GET", "POST"])
# # def speak_stream():
# #     # log request immediately
# #     try:
# #         txt = ""
# #         if request.method == "GET":
# #             txt = request.args.get("text", "") or ""
# #         else:
# #             body = request.get_json(silent=True) or {}
# #             txt = body.get("text", "") or ""
# #         current_app.logger.info("==== SPEAK-STREAM ROUTE CALLED ====")
# #         current_app.logger.info("speak-stream preview=%s len=%d", (txt[:120] + ("..." if len(txt) > 120 else "")), len(txt))
# #     except Exception as e:
# #         current_app.logger.exception("Error reading speak-stream request: %s", e)

# #     if not txt:
# #         # return early so client sees a JSON error instead of empty audio
# #         return jsonify({"error": "missing text"}), 400

# #     generator = stream_tts_from_openai(txt)    # direct_passthrough prevents Flask from buffering the whole generator
# #     return Response(generator, mimetype="audio/mpeg", direct_passthrough=True)

# # @bp.route("/speak-stream", methods=["GET", "POST"])
# # # def speak_stream():
# # #     """
# # #     Streams OpenAI TTS audio (replaces ElevenLabs).
# # #     No audio files saved - streams directly to client.
# # #     """
# # #     try:
# # #         txt = ""
# # #         if request.method == "GET":
# # #             txt = request.args.get("text", "") or ""
# # #         else:
# # #             body = request.get_json(silent=True) or {}
# # #             txt = body.get("text", "") or ""
# # #         current_app.logger.info("==== SPEAK-STREAM ROUTE CALLED ====")
# # #         current_app.logger.info("speak-stream preview=%s len=%d", (txt[:120] + ("..." if len(txt) > 120 else "")), len(txt))
# # #     except Exception as e:
# # #         current_app.logger.exception("Error reading speak-stream request: %s", e)

# # #     if not txt:
# # #         return jsonify({"error": "missing text"}), 400

# # #     # CHANGED: Use OpenAI instead of ElevenLabs
# # #     generator = stream_tts_from_openai(txt)
# # #     return Response(generator, mimetype="audio/mpeg", direct_passthrough=True)
# # def speak_stream():
# #     try:
# #         if request.method == 'GET':
# #             txt = request.args.get('text', '')
# #             current_app.logger.info(f'SPEAK-STREAM GET called with text length: {len(txt)}')
# #         else:
# #             json_data = request.get_json(silent=True)
# #             txt = json_data.get('text', '') if json_data else ''
# #             current_app.logger.info(f'SPEAK-STREAM POST called with text length: {len(txt)}')

# #         if not txt:
# #             return {"error": "Missing text parameter"}, 400

# #         # Optionally limit text length for TTS
# #         preview_len = min(len(txt), 120)
# #         preview_text = txt[:preview_len]

# #         # Generate the audio stream response from OpenAI TTS stream generator function
# #         return Response(
# #             streamttsfromopenai(txt),
# #             mimetype='audio/mpeg',
# #             direct_passthrough=True
# #         )

#     # except Exception as e:
#     #     current_app.logger.exception(f"Error in speak-stream endpoint: {e}")
#     #     return {"error": "Internal server error"}, 500

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

#         gamified = generate_gamified_prompt(current_stage, text, evolution=bool(evolution_msg))
#         question = generate_reflective_question(text, reply_to)

#         return jsonify({
#             "stage": current_stage,
#             "question": question,
#             "evolution": evolution_msg,
#             "gamified": gamified,
#             "xp_gain": xp_gain,
#             "badges": badges,
#         })
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to finalize stage"}), 500
# routes.py

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

# @bp.route('/merged', methods=['POST'])
# def merged():
#     """
#     Backend-only: ensure model references 'Mind Mirror' and 'Mission' (or both).
#     Uses existing helpers. Also performs a quiet mood/stage detection on each user message
#     and stores it in user progress (invisible to the user).
#     """
#     try:
#         data = request.json
#         entry = data.get("text", "").strip()
#         last_stage = data.get("last_stage", "").strip()
#         reply_to = data.get("reply_to", "").strip()
#         user_id = data.get("user_id")
#         if not entry:
#             return jsonify({"error": "Missing entry"}), 400

#         streak = 0
#         rewards = []
#         message_rewards = []
#         missions_completed = 0
#         new_mission_reward = None

#         if user_id:
#             streak = update_streak(user_id)
#             rewards = check_streak_rewards(user_id, streak)
#             message_rewards = check_message_rewards(user_id)

#         # Mission completion if replying to a task
#         if reply_to and user_id:
#             try:
#                 with open("daily_tasks.json") as f:
#                     tasks = json.load(f)
#                 task_to_complete = next(
#                     (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
#                     None
#                 )
#                 if task_to_complete:
#                     save_completed_task(user_id, task_to_complete)
#                     progress = get_user_progress(user_id)
#                     progress["missions_completed"] = progress.get("missions_completed", 0) + 1
#                     missions_completed = progress["missions_completed"]
#                     if missions_completed in MISSION_REWARDS:
#                         reward = MISSION_REWARDS[missions_completed]
#                         progress["xp"] += reward["xp"]
#                         if reward["badge"] not in progress.get("badges", []):
#                             progress["badges"].append(reward["badge"])
#                         new_mission_reward = reward
#                     save_user_progress(user_id, progress)
#             except Exception as e:
#                 print("⚠ Error marking growth prompt complete:", e)

#         # Save raw incoming user entry as memory
#         if user_id:
#             try:
#                 save_conversation_message(user_id, "user", entry)
#             except Exception as e:
#                 print("⚠ Warning: could not save incoming message:", e)

#         # --- Hidden: detect mood / stage from user message (backend-only, not shown to user) ---
#         if user_id:
#             try:
#                 # Small context to help classifier (fetch last few msgs quietly)
#                 try:
#                     _recent_small = get_recent_conversation(user_id, limit=3)
#                     _context_text = "\n".join([f"{m['role']}: {m['content']}" for m in _recent_small])
#                 except Exception:
#                     _context_text = ""

#                 # Run the classifier quietly (it should return stage, confidence, maybe mood)
#                 try:
#                     _classification_quiet = classify_stage(entry, context=_context_text)
#                 except TypeError:
#                     _classification_quiet = classify_stage(entry)

#                 # Extract values we care about
#                 detected_stage = _classification_quiet.get("stage")
#                 detected_confidence = float(_classification_quiet.get("confidence", 0) or 0)
#                 detected_mood = _classification_quiet.get("mood") or _classification_quiet.get("emotion") or None

#                 # Persist detection quietly in user's progress/profile (no frontend exposure)
#                 try:
#                     progress = get_user_progress(user_id)
#                     progress["_last_detected_stage"] = detected_stage
#                     progress["_last_stage_confidence"] = detected_confidence
#                     progress["_last_detected_mood"] = detected_mood
#                     progress["_last_stage_ts"] = int(time.time() * 1000)
#                     save_user_progress(user_id, progress)
#                 except Exception as e:
#                     print("⚠ Could not save quiet stage/mood metadata:", e)

#             except Exception as e:
#                 print("⚠ Mood/stage detection failed (quiet):", e)

#         # Build context messages for OpenAI
#         messages_for_ai = []
#         # persona/system message first
#         # system_msg = {
#         #     "role": "system",
#         #     "content": "You are a kind, reflective Spiral Dynamics mentor and supportive chatbot for RETVRN. Keep replies concise and empathetic."
#         # }
#         system_msg = {
#     "role": "system",
#     "content": (
#         "You are a warm, natural, conversational companion for RETVRN who speaks like a supportive friend. "
#         "Be kind and reflective, but avoid formal or robotic phrasing — use contractions, short paragraphs, and "
#         "simple everyday language. If the user has just completed a mission, briefly celebrate (1–2 lines), "
#         "then follow with an open, friendly follow-up question to keep the chat going. Keep responses human, varied, "
#         "and gently encouraging while staying concise."
#     )
# }

#         messages_for_ai.append(system_msg)

#         # Helper: parse latest assistant message for Mind Mirror and Mission
#         def _get_latest_mindmirror_mission(uid):
#             try:
#                 recent = get_recent_conversation(uid, limit=12)  # look back a bit further for mission/mindmirror
#             except Exception:
#                 return None, None
#             # search newest -> oldest
#             for m in reversed(recent):
#                 if m.get("role") == "assistant" and m.get("content"):
#                     content = m["content"]
#                     mind = None
#                     mission = None
#                     for line in content.splitlines():
#                         ln = line.strip()
#                         if ln.lower().startswith("mind mirror:"):
#                             mind = ln.split(":", 1)[1].strip()
#                         elif ln.lower().startswith("mission:"):
#                             mission = ln.split(":", 1)[1].strip()
#                     if mind or mission:
#                         return mind, mission
#             return None, None

#         # If we have a user_id, fetch recent messages and append (oldest -> newest)
#         if user_id:
#             try:
#                 recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
#                 for m in recent:
#                     r = m.get("role", "user")
#                     if r not in ("user", "assistant", "system"):
#                         r = "user"
#                     messages_for_ai.append({"role": r, "content": m.get("content", "")})
#                 # explicit assistant snippet containing latest Mind Mirror / Mission (if any)
#                 mind_mirror_text, mission_text = _get_latest_mindmirror_mission(user_id)
#                 if mind_mirror_text or mission_text:
#                     explicit_snip = (
#                         f"Latest Mind Mirror: {mind_mirror_text or '—'}\n"
#                         f"Latest Mission: {mission_text or '—'}"
#                     )
#                     # Append as assistant role to ensure visibility (won't change UI)
#                     messages_for_ai.append({"role": "assistant", "content": explicit_snip})
#             except Exception as e:
#                 print("⚠ Could not fetch recent conversation:", e)

#         # Additional system instruction to nudge model to use Mind Mirror/Mission when present
#         # messages_for_ai.insert(1, {
#         #     "role": "system",
#         #     "content": (
#         #         "When answering, first check for any 'Latest Mind Mirror' and 'Latest Mission' in the conversation. "
#         #         "If present, briefly reference them and tailor suggestions to align with that Mind Mirror and/or Mission. "
#         #         "If neither is present, answer normally and empathetically."
#         #     )
#         # })
#         messages_for_ai.insert(1, {
#     "role": "system",
#     "content": (
#         "When answering, first check for any 'Latest Mind Mirror' and 'Latest Mission' in the conversation. "
#         "If present, briefly reference them so your reply feels connected to the user's recent reflection or task. "
#         "If the user has just completed the mission, celebrate briefly (a warm, casual line), then ask a friendly, "
#         "open-ended follow-up that invites more sharing (e.g., 'How did that feel?' or 'Anything surprising?'). "
#         "Always avoid sounding formal or repetitive — aim to sound like a compassionate human companion."
#     )
# })


#         # Append the current user message last
#         current_user_content = entry if not reply_to else f"Previous: {reply_to}\nUser: {entry}"
#         messages_for_ai.append({"role": "user", "content": current_user_content})

#         # Decide intent
#         intent = detect_intent(entry)

#         # ---------------------------
#         # Chat (casual) flow
#         # ---------------------------
#         # if intent == "chat":
#         #     try:
#         #         resp = client.chat.completions.create(
#         #             model='gpt-4.1',
#         #             messages=messages_for_ai,
#         #             temperature=0.7,
#         #         )
#         #         ai_resp = resp.choices[0].message.content.strip()
#         #     except Exception as e:
#         #         print("AI chat error, falling back:", e)
#         #         try:
#         #             ai_resp = client.chat.completions.create(
#         #                 model='gpt-4.1',
#         #                 messages=[{"role": "user", "content": f"Be a kind friend and casually respond to:\n{current_user_content}"}],
#         #                 temperature=0.7
#         #             ).choices[0].message.content.strip()
#         #         except Exception as e2:
#         #             print("Fallback AI also failed:", e2)
#         #             return jsonify({"error": "AI service unavailable"}), 503

#         #     # Save assistant response
#         #     if user_id:
#         #         try:
#         #             save_conversation_message(user_id, "assistant", ai_resp)
#         #         except Exception as e:
#         #             print("⚠ Could not save assistant reply:", e)

#         #     return jsonify({
#         #         "mode": "chat",
#         #         "response": ai_resp,
#         #         "streak": streak,
#         #         "rewards": rewards,
#         #         "message_rewards": message_rewards,
#         #         "missions_completed": missions_completed,
#         #         "new_mission_reward": new_mission_reward,
#         #     })
# # ---------------------------
#         # Chat (casual) flow
#         # ---------------------------
#         if intent == "chat":
#             try:
#                 resp = client.chat.completions.create(
#                     model='gpt-4.1',
#                     messages=messages_for_ai,
#                     temperature=0.7,
#                 )
#                 ai_resp = resp.choices[0].message.content.strip()
#             except Exception as e:
#                 print("AI chat error, falling back:", e)
#                 try:
#                     ai_resp = client.chat.completions.create(
#                         model='gpt-4.1',
#                         messages=[{
#                             "role": "user",
#                             "content": f"Be a kind friend and casually respond to:\n{current_user_content}"
#                         }],
#                         temperature=0.7
#                     ).choices[0].message.content.strip()
#                 except Exception as e2:
#                     print("Fallback AI also failed:", e2)
#                     return jsonify({"error": "AI service unavailable"}), 503

#             # 🔊 TTS URL banayi ja rahi hai, sirf is response ke liye (kahi store nahi hogi)
#             base_url = request.url_root.rstrip("/")
#             tts_text = ai_resp
#             audio_url = f"{base_url}/speak-stream?text={quote_plus(tts_text)}"

#             if user_id:
#                 try:
#                     save_conversation_message(user_id, "assistant", ai_resp)
#                 except Exception as e:
#                     print("⚠ Could not save assistant reply:", e)

#             return jsonify({
#                 "mode": "chat",
#                 "response": ai_resp,
#                 "audiourl": audio_url,  # 👈 front-end isko direct use kare, Firebase me mat save karo
#                 "streak": streak,
#                 "rewards": rewards,
#                 "message_rewards": message_rewards,
#                 "missions_completed": missions_completed,
#                 "new_mission_reward": new_mission_reward,
#             })
#         # ---------------------------
#         # Spiral (reflection) flow
#         # ---------------------------
#         # Provide a small context string for classifier/question generator
#         context_text = ""
#         if user_id:
#             try:
#                 recent_small = get_recent_conversation(user_id, limit=3)
#                 context_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent_small])
#             except Exception:
#                 context_text = ""

#         # classify_stage may accept context
#         try:
#             classification = classify_stage(entry, context=context_text)
#         except TypeError:
#             classification = classify_stage(entry)

#         stage = classification.get("stage")
#         # prefer classification-provided mind mirror if available
#         mind_mirror_gen = classification.get("mind_mirror") or classification.get("mind_mirror_text") or None
#         evolution_msg = check_evolution(last_stage, classification)

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

#         # gamified prompt treated as Mission
#         gamified = generate_gamified_prompt(stage or last_stage, entry, evolution=bool(evolution_msg))

#         # generate_reflective_question - backcompat handled
#         try:
#             question = generate_reflective_question(entry, reply_to=reply_to or None, context=context_text)
#         except TypeError:
#             question = generate_reflective_question(entry, reply_to)

#         # Save assistant-generated question to conversation store
#         if user_id and question:
#             try:
#                 save_conversation_message(user_id, "assistant", question)
#             except Exception as e:
#                 print("⚠ Could not save assistant question:", e)

#         # --- Save a single structured assistant message containing Stage / Mind Mirror / Mission / Question
#         if user_id:
#             try:
#                 # Build parseable block; prefer generated mind mirror, fallback to latest saved one if present
#                 mm = mind_mirror_gen
#                 prev_mind = None
#                 prev_mission = None
#                 if not mm:
#                     # try to fetch existing latest Mind Mirror from previous assistant messages
#                     prev_mind, prev_mission = _get_latest_mindmirror_mission(user_id)
#                     if prev_mind:
#                         mm = prev_mind

#                 mission_text_block = gamified or (prev_mission if prev_mission else None)
#                 mission_lines = [
#                     f"Stage: {stage or last_stage}",
#                     f"Mind Mirror: {mm or '—'}",
#                     f"Mission: {mission_text_block or '—'}",
#                     f"Question: {question or '—'}"
#                 ]
#                 mission_block = "\n".join([ln for ln in mission_lines if ln.strip()])
#                 save_conversation_message(user_id, "assistant", mission_block)
#             except Exception as e:
#                 print("⚠ Could not save mission/mind-mirror block:", e)

#             # 🔊 Spiral reply ke liye TTS text
#         tts_parts = []
#         if stage:
#             tts_parts.append(f"Stage {stage}.")
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
#         spiral_audio_url = (
#             f"{base_url}/speak-stream?text={quote_plus(tts_text)}"
#             if tts_text else None
#         )

#         response = {
#             "mode": "spiral",
#             "stage": stage,
#             "evolution": evolution_msg,
#             "xp_gain": xp_gain,
#             "badges": badges,
#             "question": question,
#             "gamified": gamified,
#             "confidence": classification.get("confidence"),
#             "reason": classification.get("reason"),
#             "streak": streak,
#             "rewards": rewards,
#             "message_rewards": message_rewards,
#             "missions_completed": missions_completed,
#             "new_mission_reward": new_mission_reward,
#             "audiourl": spiral_audio_url,
#         }
#         if classification.get("confidence", 1) < 0.7 and classification.get("secondary"):
#             response["note"] = f"Also detected: {classification['secondary']}"
#         return jsonify(response)

#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to process reflection"}), 500


# # @bp.route('/reflect_transcription', methods=['POST'])
# # def reflect_transcription():
# #     try:
# #         if 'audio' not in request.files:
# #             return jsonify({"error": "Missing audio file"}), 400
# #         reply_to = request.form.get("reply_to", "")
# #         last_stage = request.form.get("last_stage", "")
# #         user_id = request.form.get("user_id", "")
# #         audio_file = request.files['audio']
# @bp.route('/reflect_transcription', methods=['POST'])
# def reflect_transcription():
#     try:
#         if 'audio' not in request.files:
#             return jsonify({"error": "Missing audio file"}), 400
#         reply_to = request.form.get("reply_to", "")
#         last_stage = request.form.get("last_stage", "")
#         user_id = request.form.get("user_id", "")
#         # 🔹 voice mode se aaya force flag
#         force_spiral_flag = request.form.get("force_spiral", "").lower() == "true"
#         audio_file = request.files['audio']

#         streak = 0
#         rewards = []
#         message_rewards = []
#         missions_completed = 0
#         new_mission_reward = None

#         if user_id:
#             streak = update_streak(user_id)
#             rewards = check_streak_rewards(user_id, streak)
#             message_rewards = check_message_rewards(user_id)

#         # ✅ Mission tracking if replying (audio)
#         if reply_to and user_id:
#             try:
#                 with open("daily_tasks.json") as f:
#                     tasks = json.load(f)
#                 task_to_complete = next(
#                     (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
#                     None
#                 )
#                 if task_to_complete:
#                     save_completed_task(user_id, task_to_complete)

#                     # Increment missions completed
#                     progress = get_user_progress(user_id)
#                     progress["missions_completed"] = progress.get("missions_completed", 0) + 1
#                     missions_completed = progress["missions_completed"]

#                     # Check mission milestone rewards
#                     if missions_completed in MISSION_REWARDS:
#                         reward = MISSION_REWARDS[missions_completed]
#                         progress["xp"] += reward["xp"]
#                         if reward["badge"] not in progress.get("badges", []):
#                             progress["badges"].append(reward["badge"])
#                         new_mission_reward = reward
#                     save_user_progress(user_id, progress)
#             except Exception as e:
#                 print("⚠ Error marking growth prompt complete (audio):", e)

#         filename = f"{user_id or 'anon'}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.wav"
#         os.makedirs("audios", exist_ok=True)
#         path = os.path.join("audios", filename)
#         audio_file.save(path)

#         upload_resp = requests.post(
#             "https://api.assemblyai.com/v2/upload",
#             headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY"), "content-type": "application/octet-stream"},
#             data=open(path, "rb")
#         )
#         audio_url = upload_resp.json().get("upload_url")
#         transcript_post = requests.post(
#             "https://api.assemblyai.com/v2/transcript",
#             headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
#             json={"audio_url": audio_url, "speaker_labels": True}
#         )
#         transcript_id = transcript_post.json().get("id")

#         while True:
#             poll_resp = requests.get(
#                 f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
#                 headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
#             )
#             poll_data = poll_resp.json()
#             if poll_data.get("status") in ("completed", "error"):
#                 break

#         if poll_data.get("status") == "error":
#             return jsonify({"error": "Transcription failed"}), 500

#         # transcript_text = poll_data.get("text", "")
#         transcript_text = poll_data.get("text", "") or ""
#         # utterances = poll_data.get("utterances", [])
#         utterances = poll_data.get("utterances") or []
#         # dialogue = "\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in utterances)
#         dialogue = "\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in utterances)


#         if utterances:
#             dialogue = "\n".join(
#             f"Speaker {u.get('speaker')}: {u.get('text','')}" for u in utterances
#              )
#         else:
#     # diarization nahi mili, simple single-speaker transcript use karo
#             dialogue = transcript_text
#         # intent = detect_intent(transcript_text)
#         # if intent == "chat":
#         #     ai_resp = client.chat.completions.create(
#         #         model='gpt-4.1',
#         #         messages=[{"role": "user", "content": f"Carefully respond to:\n{dialogue}"}],
#         #         temperature=0.7,
#         #     ).choices[0].message.content.strip()
#         #     return jsonify({
#         #         "mode": "chat",
#         #         "response": ai_resp,
#         #         "transcription": dialogue,
#         #         "diarized": True,
#         #         "streak": streak,
#         #         "rewards": rewards,
#         #         "message_rewards": message_rewards,
#         #         "missions_completed": missions_completed,
#         #         "new_mission_reward": new_mission_reward,
#         #     })
#         # intent = detect_intent(transcript_text)
#         # if intent == "chat":
#         #     ai_resp = client.chat.completions.create(
#         #         model='gpt-4.1',
#         #         messages=[{"role": "user", "content": f"Carefully respond to:\n{dialogue}"}],
#         #         temperature=0.7,
#         #     ).choices[0].message.content.strip()
            
#         #     base_url = request.url_root.rstrip("/")
#         #     tts_text = ai_resp
#         #     audio_url = f"{base_url}/speak-stream?text={quote_plus(tts_text)}"

#         #     return jsonify({
#         #         "mode": "chat",
#         #         "response": ai_resp,
#         #         "audiourl": audio_url,  # 👈 sirf client ke liye
#         #         "transcription": dialogue,
#         #         "diarized": True,
#         #         "streak": streak,
#         #         "rewards": rewards,
#         #         "message_rewards": message_rewards,
#         #         "missions_completed": missions_completed,
#         #         "new_mission_reward": new_mission_reward,
#         #     })
#         # # speaker_texts = defaultdict(str)
#         # # for u in utterances:
#         # #     speaker_name = f"Speaker {u['speaker']}"
#         # #     speaker_texts[speaker_name] += u["text"] + " "
#         # speaker_texts = defaultdict(str)
#         # for u in utterances:
#         #     speaker_name = f"Speaker {u.get('speaker')}"
#         #     speaker_texts[speaker_name] += (u.get("text", "") + " ")

#         # speaker_stages = {}
#         # for speaker_name, text in speaker_texts.items():
#         #     try:
#         #         stage_info = classify_stage(text.strip())
#         #         speaker_stages[speaker_name] = {"stage": stage_info["stage"], "text": text.strip()}
#         #     except Exception as e:
#         #         speaker_stages[speaker_name] = {"stage": "Unknown", "text": text.strip(), "error": str(e)}

#         # return jsonify({
#         #     "mode": "spiral",
#         #     "transcription": dialogue,
#         #     "speaker_stages": speaker_stages,
#         #     "diarized": True,
#         #     "ask_speaker_pick": True,
#         #     "streak": streak,
#         #     "rewards": rewards,
#         #     "message_rewards": message_rewards,
#         #     "missions_completed": missions_completed,
#         #     "new_mission_reward": new_mission_reward,
#         # })
#         intent = detect_intent(transcript_text)

#         # 🔹 agar voice mode ne force_spiral bheja hai to hamesha spiral hi lo
#         if force_spiral_flag:
#             intent = "spiral"

#         if intent == "chat":
#             ai_resp = client.chat.completions.create(
#                 model='gpt-4.1',
#                 messages=[{"role": "user", "content": f"Carefully respond to:\n{dialogue}"}],
#                 temperature=0.7,
#             ).choices[0].message.content.strip()
#             return jsonify({
#                 "mode": "chat",
#                 "response": ai_resp,
#                 "transcription": dialogue,
#                 "diarized": True,
#                 "streak": streak,
#                 "rewards": rewards,
#                 "message_rewards": message_rewards,
#                 "missions_completed": missions_completed,
#                 "new_mission_reward": new_mission_reward,
#             })

#         # 👇 yahan se tumhara existing spiral / speaker_stages wala code same rahe
#         speaker_texts = defaultdict(str)
#         for u in utterances:
#             speaker_name = f"Speaker {u['speaker']}"
#             speaker_texts[speaker_name] += u["text"] + " "

#         speaker_stages = {}
#         for speaker_name, text in speaker_texts.items():
#             try:
#                 stage_info = classify_stage(text.strip())
#                 speaker_stages[speaker_name] = {
#                     "stage": stage_info["stage"],
#                     "text": text.strip()
#                 }
#             except Exception as e:
#                 speaker_stages[speaker_name] = {
#                     "stage": "Unknown",
#                     "text": text.strip(),
#                     "error": str(e),
#                 }

#         return jsonify({
#             "mode": "spiral",
#             "transcription": dialogue,
#             "speaker_stages": speaker_stages,
#             "diarized": True,
#             "ask_speaker_pick": True,
#             "streak": streak,
#             "rewards": rewards,
#             "message_rewards": message_rewards,
#             "missions_completed": missions_completed,
#             "new_mission_reward": new_mission_reward,
#         })
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to process transcription"}), 500


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
from flask import Blueprint, request, jsonify, Response, current_app
import json
import os
import traceback
from datetime import datetime
from collections import defaultdict
import requests
import time
from urllib.parse import quote_plus

from tasks import generate_daily_task, save_completed_task, get_user_tasks
from rewards import (
    get_user_progress,
    save_user_progress,
    update_streak,
    check_streak_rewards,
    check_message_rewards,
)
from spiral_dynamics import (
    detect_intent,
    classify_stage,
    check_evolution,
    generate_reflective_question,
    generate_gamified_prompt,
    client,
)
from firebase_utils import db, save_conversation_message, get_recent_conversation
from notifications import send_welcome_notification
from tts import stream_tts_from_openai  # OpenAI TTS streamer

bp = Blueprint("main", __name__)  # ✅ yahan __name__ hi use karna hai

AUDIO_FOLDER = "audios"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# How many last messages to include as context (adjust as needed)
HISTORY_LIMIT = 6

XP_REWARDS = {
    "level_up": 10,
    "daily_streak_3": 15,
    "daily_streak_7": 30,
    "daily_streak_14": 50,
    "daily_streak_30": 100,
    "message_streak": 20,
}

BADGES = {
    "level_up": "🌱 Level Up",
    "daily_streak_3": "🔥 3-Day Streak",
    "daily_streak_7": "🌟 Weekly Explorer",
    "daily_streak_14": "🌙 Fortnight Champion",
    "daily_streak_30": "🌕 Monthly Master",
    "message_streak": "💬 Chatterbox",
}

# ✅ New mission milestone rewards
MISSION_REWARDS = {
    1: {"xp": 20, "badge": "🎯 First Mission"},
    5: {"xp": 50, "badge": "🏅 Mission Explorer"},
    10: {"xp": 100, "badge": "🚀 Mission Master"},
}


@bp.route('/')
def home():
    return "Backend is running"


@bp.route('/daily_task', methods=['GET'])
def daily_task():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    try:
        task = generate_daily_task()
        with open("completed_tasks.json") as f:
            completed = json.load(f)
        user_done = any(
            t for t in completed if t.get("user_id") == user_id and t.get("date") == task.get("date") and t.get("completed")
        )
        task["user_done"] = user_done
        return jsonify(task)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch daily task"}), 500


@bp.route('/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    user_id = data.get("user_id")
    task_id = data.get("task_id")
    if not user_id or not task_id:
        return jsonify({"error": "Missing user_id or task_id"}), 400
    try:
        with open("daily_tasks.json") as f:
            tasks = json.load(f)
        task_to_complete = next((t for t in tasks if str(t.get("timestamp")) == task_id and t.get("user_id") == user_id), None)
        if not task_to_complete:
            return jsonify({"error": "Task not found"}), 404
        task_to_complete["completed"] = True
        task_to_complete["completion_timestamp"] = datetime.utcnow().isoformat()
        with open("daily_tasks.json", "w") as f:
            json.dump(tasks, f, indent=2)
        save_completed_task(user_id, task_to_complete)
        return jsonify({"message": "Task marked completed"})
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to complete task"}), 500


@bp.route('/task_history', methods=['GET'])
def task_history():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    try:
        tasks = get_user_tasks(user_id, "completed_tasks.json")
        return jsonify(tasks)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch task history"}), 500


@bp.route('/user_progress', methods=['GET'])
def user_progress():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    try:
        progress = get_user_progress(user_id)
        return jsonify(progress)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch user progress"}), 500

@bp.route('/merged', methods=['POST'])
def merged():
    """
    Backend-only: ensure model references 'Mind Mirror' and 'Mission' (or both).
    Uses existing helpers. Also performs a quiet mood/stage detection on each user message
    and stores it in user progress (invisible to the user).
    """
    try:
        data = request.json
        entry = data.get("text", "").strip()
        last_stage = data.get("last_stage", "").strip()
        reply_to = data.get("reply_to", "").strip()
        user_id = data.get("user_id")
        if not entry:
            return jsonify({"error": "Missing entry"}), 400

        streak = 0
        rewards = []
        message_rewards = []
        missions_completed = 0
        new_mission_reward = None

        if user_id:
            streak = update_streak(user_id)
            rewards = check_streak_rewards(user_id, streak)
            message_rewards = check_message_rewards(user_id)

        # Mission completion if replying to a task
        if reply_to and user_id:
            try:
                with open("daily_tasks.json") as f:
                    tasks = json.load(f)
                task_to_complete = next(
                    (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
                    None
                )
                if task_to_complete:
                    save_completed_task(user_id, task_to_complete)
                    progress = get_user_progress(user_id)
                    progress["missions_completed"] = progress.get("missions_completed", 0) + 1
                    missions_completed = progress["missions_completed"]
                    if missions_completed in MISSION_REWARDS:
                        reward = MISSION_REWARDS[missions_completed]
                        progress["xp"] += reward["xp"]
                        if reward["badge"] not in progress.get("badges", []):
                            progress["badges"].append(reward["badge"])
                        new_mission_reward = reward
                    save_user_progress(user_id, progress)
            except Exception as e:
                print("⚠ Error marking growth prompt complete:", e)

        # Save raw incoming user entry as memory
        if user_id:
            try:
                save_conversation_message(user_id, "user", entry)
            except Exception as e:
                print("⚠ Warning: could not save incoming message:", e)

        # --- Hidden: detect mood / stage from user message (backend-only, not shown to user) ---
        if user_id:
            try:
                # Small context to help classifier (fetch last few msgs quietly)
                try:
                    _recent_small = get_recent_conversation(user_id, limit=3)
                    _context_text = "\n".join([f"{m['role']}: {m['content']}" for m in _recent_small])
                except Exception:
                    _context_text = ""

                # Run the classifier quietly (it should return stage, confidence, maybe mood)
                try:
                    _classification_quiet = classify_stage(entry, context=_context_text)
                except TypeError:
                    _classification_quiet = classify_stage(entry)

                # Extract values we care about
                detected_stage = _classification_quiet.get("stage")
                detected_confidence = float(_classification_quiet.get("confidence", 0) or 0)
                detected_mood = _classification_quiet.get("mood") or _classification_quiet.get("emotion") or None

                # Persist detection quietly in user's progress/profile (no frontend exposure)
                try:
                    progress = get_user_progress(user_id)
                    progress["_last_detected_stage"] = detected_stage
                    progress["_last_stage_confidence"] = detected_confidence
                    progress["_last_detected_mood"] = detected_mood
                    progress["_last_stage_ts"] = int(time.time() * 1000)
                    save_user_progress(user_id, progress)
                except Exception as e:
                    print("⚠ Could not save quiet stage/mood metadata:", e)

            except Exception as e:
                print("⚠ Mood/stage detection failed (quiet):", e)

        # Build context messages for OpenAI
        messages_for_ai = []
        
        system_msg = {
    "role": "system",
    "content": (
        "You are a warm, natural, conversational companion for RETVRN who speaks like a supportive friend. "
        "Be kind and reflective, but avoid formal or robotic phrasing — use contractions, short paragraphs, and "
        "simple everyday language. If the user has just completed a mission, briefly celebrate (1–2 lines), "
        "then follow with an open, friendly follow-up question to keep the chat going. Keep responses human, varied, "
        "and gently encouraging while staying concise."
    )
}

        messages_for_ai.append(system_msg)

        # Helper: parse latest assistant message for Mind Mirror and Mission
        def _get_latest_mindmirror_mission(uid):
            try:
                recent = get_recent_conversation(uid, limit=12)  # look back a bit further for mission/mindmirror
            except Exception:
                return None, None
            # search newest -> oldest
            for m in reversed(recent):
                if m.get("role") == "assistant" and m.get("content"):
                    content = m["content"]
                    mind = None
                    mission = None
                    for line in content.splitlines():
                        ln = line.strip()
                        if ln.lower().startswith("mind mirror:"):
                            mind = ln.split(":", 1)[1].strip()
                        elif ln.lower().startswith("mission:"):
                            mission = ln.split(":", 1)[1].strip()
                    if mind or mission:
                        return mind, mission
            return None, None

        # If we have a user_id, fetch recent messages and append (oldest -> newest)
        if user_id:
            try:
                recent = get_recent_conversation(user_id, limit=HISTORY_LIMIT)
                for m in recent:
                    r = m.get("role", "user")
                    if r not in ("user", "assistant", "system"):
                        r = "user"
                    messages_for_ai.append({"role": r, "content": m.get("content", "")})
                # explicit assistant snippet containing latest Mind Mirror / Mission (if any)
                mind_mirror_text, mission_text = _get_latest_mindmirror_mission(user_id)
                if mind_mirror_text or mission_text:
                    explicit_snip = (
                        f"Latest Mind Mirror: {mind_mirror_text or '—'}\n"
                        f"Latest Mission: {mission_text or '—'}"
                    )
                    # Append as assistant role to ensure visibility (won't change UI)
                    messages_for_ai.append({"role": "assistant", "content": explicit_snip})
            except Exception as e:
                print("⚠ Could not fetch recent conversation:", e)

        messages_for_ai.insert(1, {
    "role": "system",
    "content": (
        "When answering, first check for any 'Latest Mind Mirror' and 'Latest Mission' in the conversation. "
        "If present, briefly reference them so your reply feels connected to the user's recent reflection or task. "
        "If the user has just completed the mission, celebrate briefly (a warm, casual line), then ask a friendly, "
        "open-ended follow-up that invites more sharing (e.g., 'How did that feel?' or 'Anything surprising?'). "
        "Always avoid sounding formal or repetitive — aim to sound like a compassionate human companion."
    )
})


        # Append the current user message last
        current_user_content = entry if not reply_to else f"Previous: {reply_to}\nUser: {entry}"
        messages_for_ai.append({"role": "user", "content": current_user_content})

        # Decide intent
        intent = detect_intent(entry)

        if intent == "chat":
            try:
                resp = client.chat.completions.create(
                    model='gpt-4.1',
                    messages=messages_for_ai,
                    temperature=0.7,
                )
                ai_resp = resp.choices[0].message.content.strip()
            except Exception as e:
                print("AI chat error, falling back:", e)
                try:
                    ai_resp = client.chat.completions.create(
                        model='gpt-4.1',
                        messages=[{
                            "role": "user",
                            "content": f"Be a kind friend and casually respond to:\n{current_user_content}"
                        }],
                        temperature=0.7
                    ).choices[0].message.content.strip()
                except Exception as e2:
                    print("Fallback AI also failed:", e2)
                    return jsonify({"error": "AI service unavailable"}), 503

            # 🔊 TTS URL banayi ja rahi hai, sirf is response ke liye (kahi store nahi hogi)
            base_url = request.url_root.rstrip("/")
            tts_text = ai_resp
            audio_url = f"{base_url}/speak-stream?text={quote_plus(tts_text)}"

            if user_id:
                try:
                    save_conversation_message(user_id, "assistant", ai_resp)
                except Exception as e:
                    print("⚠ Could not save assistant reply:", e)

            return jsonify({
                "mode": "chat",
                "response": ai_resp,
                "audiourl": audio_url,  # 👈 front-end isko direct use kare, Firebase me mat save karo
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
                "missions_completed": missions_completed,
                "new_mission_reward": new_mission_reward,
            })
        # ---------------------------
        # Spiral (reflection) flow
        # ---------------------------
        # Provide a small context string for classifier/question generator
        context_text = ""
        if user_id:
            try:
                recent_small = get_recent_conversation(user_id, limit=3)
                context_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent_small])
            except Exception:
                context_text = ""

        # classify_stage may accept context
        try:
            classification = classify_stage(entry, context=context_text)
        except TypeError:
            classification = classify_stage(entry)

        stage = classification.get("stage")
        # prefer classification-provided mind mirror if available
        mind_mirror_gen = classification.get("mind_mirror") or classification.get("mind_mirror_text") or None
        evolution_msg = check_evolution(last_stage, classification)

        xp_gain = 0
        badges = []
        if user_id and evolution_msg:
            progress = get_user_progress(user_id)
            progress["xp"] += XP_REWARDS.get("level_up", 10)
            if "level_up" not in progress.get("badges", []):
                progress["badges"].append("level_up")
                badges.append("🌱 Level Up")
            save_user_progress(user_id, progress)
            xp_gain = XP_REWARDS.get("level_up", 10)

        # gamified prompt treated as Mission
        gamified = generate_gamified_prompt(stage or last_stage, entry, evolution=bool(evolution_msg))

        # generate_reflective_question - backcompat handled
        try:
            question = generate_reflective_question(entry, reply_to=reply_to or None, context=context_text)
        except TypeError:
            question = generate_reflective_question(entry, reply_to)

        # Save assistant-generated question to conversation store
        if user_id and question:
            try:
                save_conversation_message(user_id, "assistant", question)
            except Exception as e:
                print("⚠ Could not save assistant question:", e)

        # --- Save a single structured assistant message containing Stage / Mind Mirror / Mission / Question
        if user_id:
            try:
                # Build parseable block; prefer generated mind mirror, fallback to latest saved one if present
                mm = mind_mirror_gen
                prev_mind = None
                prev_mission = None
                if not mm:
                    # try to fetch existing latest Mind Mirror from previous assistant messages
                    prev_mind, prev_mission = _get_latest_mindmirror_mission(user_id)
                    if prev_mind:
                        mm = prev_mind

                mission_text_block = gamified or (prev_mission if prev_mission else None)
                mission_lines = [
                    f"Stage: {stage or last_stage}",
                    f"Mind Mirror: {mm or '—'}",
                    f"Mission: {mission_text_block or '—'}",
                    f"Question: {question or '—'}"
                ]
                mission_block = "\n".join([ln for ln in mission_lines if ln.strip()])
                save_conversation_message(user_id, "assistant", mission_block)
            except Exception as e:
                print("⚠ Could not save mission/mind-mirror block:", e)

            # 🔊 Spiral reply ke liye TTS text
        tts_parts = []
        if stage:
            tts_parts.append(f"Stage {stage}.")
        if evolution_msg:
            tts_parts.append(evolution_msg)
        if question:
            tts_parts.append(f"Mind Mirror question: {question}")
        if gamified:
            gq = gamified.get("gamified_question") or ""
            gp = gamified.get("gamified_prompt") or ""
            if gq:
                tts_parts.append(gq)
            if gp:
                tts_parts.append(gp)

        tts_text = " ".join(p for p in tts_parts if p)
        base_url = request.url_root.rstrip("/")
        spiral_audio_url = (
            f"{base_url}/speak-stream?text={quote_plus(tts_text)}"
            if tts_text else None
        )

        response = {
            "mode": "spiral",
            "stage": stage,
            "evolution": evolution_msg,
            "xp_gain": xp_gain,
            "badges": badges,
            "question": question,
            "gamified": gamified,
            "confidence": classification.get("confidence"),
            "reason": classification.get("reason"),
            "streak": streak,
            "rewards": rewards,
            "message_rewards": message_rewards,
            "missions_completed": missions_completed,
            "new_mission_reward": new_mission_reward,
            "audiourl": spiral_audio_url,
        }
        if classification.get("confidence", 1) < 0.7 and classification.get("secondary"):
            response["note"] = f"Also detected: {classification['secondary']}"
        return jsonify(response)

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to process reflection"}), 500


@bp.route('/reflect_transcription', methods=['POST'])
def reflect_transcription():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Missing audio file"}), 400
        reply_to = request.form.get("reply_to", "")
        last_stage = request.form.get("last_stage", "")
        user_id = request.form.get("user_id", "")
        audio_file = request.files['audio']

        streak = 0
        rewards = []
        message_rewards = []
        missions_completed = 0
        new_mission_reward = None

        if user_id:
            streak = update_streak(user_id)
            rewards = check_streak_rewards(user_id, streak)
            message_rewards = check_message_rewards(user_id)

        # ✅ Mission tracking if replying (audio)
        if reply_to and user_id:
            try:
                with open("daily_tasks.json") as f:
                    tasks = json.load(f)
                task_to_complete = next(
                    (t for t in tasks if t.get("task") == reply_to or str(t.get("timestamp")) == reply_to),
                    None
                )
                if task_to_complete:
                    save_completed_task(user_id, task_to_complete)

                    # Increment missions completed
                    progress = get_user_progress(user_id)
                    progress["missions_completed"] = progress.get("missions_completed", 0) + 1
                    missions_completed = progress["missions_completed"]

                    # Check mission milestone rewards
                    if missions_completed in MISSION_REWARDS:
                        reward = MISSION_REWARDS[missions_completed]
                        progress["xp"] += reward["xp"]
                        if reward["badge"] not in progress.get("badges", []):
                            progress["badges"].append(reward["badge"])
                        new_mission_reward = reward
                    save_user_progress(user_id, progress)
            except Exception as e:
                print("⚠ Error marking growth prompt complete (audio):", e)

        filename = f"{user_id or 'anon'}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.wav"
        os.makedirs("audios", exist_ok=True)
        path = os.path.join("audios", filename)
        audio_file.save(path)

        upload_resp = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY"), "content-type": "application/octet-stream"},
            data=open(path, "rb")
        )
        audio_url = upload_resp.json().get("upload_url")
        transcript_post = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
            json={"audio_url": audio_url, "speaker_labels": True}
        )
        transcript_id = transcript_post.json().get("id")

        while True:
            poll_resp = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers={"authorization": os.getenv("ASSEMBLYAI_API_KEY")},
            )
            poll_data = poll_resp.json()
            if poll_data.get("status") in ("completed", "error"):
                break

        if poll_data.get("status") == "error":
            return jsonify({"error": "Transcription failed"}), 500

        # transcript_text = poll_data.get("text", "")
        transcript_text = poll_data.get("text", "") or ""
        # utterances = poll_data.get("utterances", [])
        utterances = poll_data.get("utterances") or []
        # dialogue = "\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in utterances)
        dialogue = "\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in utterances)


        if utterances:
            dialogue = "\n".join(
            f"Speaker {u.get('speaker')}: {u.get('text','')}" for u in utterances
             )
        else:
    # diarization nahi mili, simple single-speaker transcript use karo
            dialogue = transcript_text
   
        intent = detect_intent(transcript_text)
        if intent == "chat":
            ai_resp = client.chat.completions.create(
                model='gpt-4.1',
                messages=[{"role": "user", "content": f"Carefully respond to:\n{dialogue}"}],
                temperature=0.7,
            ).choices[0].message.content.strip()
            
            base_url = request.url_root.rstrip("/")
            tts_text = ai_resp
            audio_url = f"{base_url}/speak-stream?text={quote_plus(tts_text)}"

            return jsonify({
                "mode": "chat",
                "response": ai_resp,
                "audiourl": audio_url,  # 👈 sirf client ke liye
                "transcription": dialogue,
                "diarized": True,
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
                "missions_completed": missions_completed,
                "new_mission_reward": new_mission_reward,
            })
        # speaker_texts = defaultdict(str)
        # for u in utterances:
        #     speaker_name = f"Speaker {u['speaker']}"
        #     speaker_texts[speaker_name] += u["text"] + " "
        speaker_texts = defaultdict(str)
        for u in utterances:
            speaker_name = f"Speaker {u.get('speaker')}"
            speaker_texts[speaker_name] += (u.get("text", "") + " ")

        speaker_stages = {}
        for speaker_name, text in speaker_texts.items():
            try:
                stage_info = classify_stage(text.strip())
                speaker_stages[speaker_name] = {"stage": stage_info["stage"], "text": text.strip()}
            except Exception as e:
                speaker_stages[speaker_name] = {"stage": "Unknown", "text": text.strip(), "error": str(e)}

        return jsonify({
            "mode": "spiral",
            "transcription": dialogue,
            "speaker_stages": speaker_stages,
            "diarized": True,
            "ask_speaker_pick": True,
            "streak": streak,
            "rewards": rewards,
            "message_rewards": message_rewards,
            "missions_completed": missions_completed,
            "new_mission_reward": new_mission_reward,
        })
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to process transcription"}), 500
# new endpoint for audio stream
@bp.route("/speak-stream", methods=["GET", "POST"])
def speak_stream():
    """
    Streams OpenAI TTS audio as MP3.
    Koi file save nahi hoti, sirf generator se bytes stream hote hain.
    """
    try:
        if request.method == "GET":
            txt = request.args.get("text", "") or ""
        else:
            body = request.get_json(silent=True) or {}
            txt = body.get("text", "") or ""

        current_app.logger.info("==== SPEAK-STREAM ROUTE CALLED ====")
        preview = txt[:120] + ("..." if len(txt) > 120 else "")
        current_app.logger.info("speak-stream preview=%s len=%d", preview, len(txt))

        if not txt.strip():
            return jsonify({"error": "missing text"}), 400

        # OpenAI TTS generator se stream karo (tts.py se)
        generator = stream_tts_from_openai(txt)

        return Response(generator, mimetype="audio/mpeg", direct_passthrough=True)

    except Exception as e:
        current_app.logger.exception(f"Error in speak-stream endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@bp.route('/finalize_stage', methods=['POST'])
def finalize_stage():
    try:
        data = request.json
        speaker_id = data.get("speaker_id")
        speaker_stages = data.get("speaker_stages", {})
        last_stage = data.get("last_stage", "")
        reply_to = data.get("reply_to", "")
        user_id = data.get("user_id")

        if speaker_id not in speaker_stages:
            return jsonify({"error": "Speaker not found"}), 400

        speaker_info = speaker_stages[speaker_id]
        current_stage = speaker_info.get("stage", "Unknown")
        text = speaker_info.get("text", "")
        evolution_msg = check_evolution(last_stage, {"stage": current_stage})

        xp_gain = 0
        badges = []
        if user_id and evolution_msg:
            progress = get_user_progress(user_id)
            progress["xp"] += XP_REWARDS.get("level_up", 10)
            if "level_up" not in progress.get("badges", []):
                progress["badges"].append("level_up")
                badges.append("🌱 Level Up")
            save_user_progress(user_id, progress)
            xp_gain = XP_REWARDS.get("level_up", 10)

        # gamified = generate_gamified_prompt(current_stage, text, evolution=bool(evolution_msg))
        gamified = generate_gamified_prompt(current_stage, text, evolution=bool(evolution_msg))
        question = generate_reflective_question(text, reply_to)

        # 🔊 Finalized stage ke liye TTS text
        tts_parts = []
        if current_stage:
            tts_parts.append(f"Stage {current_stage}.")
        if evolution_msg:
            tts_parts.append(evolution_msg)
        if question:
            tts_parts.append(f"Mind Mirror question: {question}")
        if gamified:
            gq = gamified.get("gamified_question") or ""
            gp = gamified.get("gamified_prompt") or ""
            if gq:
                tts_parts.append(gq)
            if gp:
                tts_parts.append(gp)

        tts_text = " ".join(p for p in tts_parts if p)
        base_url = request.url_root.rstrip("/")
        audio_url = (
            f"{base_url}/speak-stream?text={quote_plus(tts_text)}"
            if tts_text else None
        )
        question = generate_reflective_question(text, reply_to)

        return jsonify({
            "stage": current_stage,
            "question": question,
            "evolution": evolution_msg,
            "gamified": gamified,
            "xp_gain": xp_gain,
            "badges": badges,
            "audiourl": audio_url,
        })
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to finalize stage"}), 500