# from flask import Blueprint, request, jsonify
# import json
# from datetime import datetime

# # Import your local modules (adjust import names if needed)
# from tasks import generate_daily_task, save_completed_task
# from rewards import get_user_progress, save_user_progress, update_streak, check_streak_rewards, check_message_rewards
# from spiral_dynamics import detect_intent, classify_stage, check_evolution
# from notifications import send_daily_task_notification
# from firebase_utils import db

# bp = Blueprint('main', __name__)

# @bp.route("/", methods=["GET"])
# def home():
#     return "Backend is running!"

# @bp.route("/daily_task", methods=["GET"])
# def get_daily_task_route():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400
#     task_data = generate_daily_task()

#     # Check user completed this task
#     try:
#         with open("completed_tasks.json", "r") as f:
#             completed_tasks = json.load(f)
#     except:
#         completed_tasks = []

#     user_completed = any(
#         t.get("user_id") == user_id and
#         t.get("date") == task_data.get("date") and
#         t.get("completed")
#         for t in completed_tasks
#     )
#     task_data["user_completed"] = user_completed
#     return jsonify(task_data)

# @bp.route("/complete_task", methods=["POST"])
# def complete_task_route():
#     data = request.get_json()
#     user_id = data.get("user_id")
#     task_id = data.get("task_id")

#     if not user_id or not task_id:
#         return jsonify({"error": "Missing user_id or task_id"}), 400

#     try:
#         with open("daily_tasks.json", "r") as f:
#             daily_tasks = json.load(f)
#     except:
#         return jsonify({"error": "Error reading daily tasks"}), 500

#     task_to_complete = None
#     for task in daily_tasks:
#         if str(task.get("timestamp")) == task_id and task.get("user_id") == user_id:
#             task["completed"] = True
#             task["completion_timestamp"] = datetime.utcnow().isoformat()
#             task_to_complete = task
#             break

#     if not task_to_complete:
#         return jsonify({"error": "Task not found"}), 404

#     with open("daily_tasks.json", "w") as f:
#         json.dump(daily_tasks, f, indent=2)

#     save_completed_task(user_id, task_to_complete)
#     return jsonify({"message": "Task marked as completed"})

# @bp.route("/task_history", methods=["GET"])
# def task_history_route():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400

#     try:
#         with open("completed_tasks.json", "r") as f:
#             completed_tasks = json.load(f)
#     except:
#         completed_tasks = []

#     user_tasks = [t for t in completed_tasks if t.get("user_id") == user_id]
#     return jsonify(user_tasks)

# @bp.route("/user_progress", methods=["GET"])
# def user_progress_route():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400
#     progress = get_user_progress(user_id)
#     return jsonify(progress)

# @bp.route("/merged", methods=["POST"])
# def merged_reflection_route():
#     data = request.get_json()
#     entry = data.get("text", "").strip()
#     last_stage = data.get("last_stage", "").strip()
#     reply_to = data.get("reply_to", "").strip()
#     user_id = data.get("user_id")

#     if not entry:
#         return jsonify({"error": "Missing journaling input."}), 400

#     streak = 0
#     streak_rewards = []
#     message_rewards = []
#     if user_id:
#         streak = update_streak(user_id)
#         streak_rewards = check_streak_rewards(user_id, streak)
#         message_rewards = check_message_rewards(user_id)

#     intent = detect_intent(entry)

#     if intent == "chat":
#         # For now, simple reply, replace with your OpenAI integration
#         reply = f"Echo: {entry}"
#         response_data = {
#             "mode": "chat",
#             "response": reply,
#             "streak": streak,
#             "rewards": streak_rewards,
#             "message_rewards": message_rewards,
#         }
#         return jsonify(response_data)

#     stage_result = _stage(entry)
#     current_stage = stage_result["stage"]
#     evolution_msg = check_evolution(last_stage, stage_result)

#     xp_gained = 0
#     badges_earned = []
#     if user_id and evolution_msg:
#         progress = get_user_progress(user_id)
#         progress["xp"] += 10  # example XP reward for level up
#         if "level_up" not in progress.get("badges", []):
#             progress["badges"].append("level_up")
#             badges_earned.append("🌱 Level Up")
#         xp_gained = 10
#         save_user_progress(user_id, progress)

#     response_data = {
#         "mode": "spiral",
#         "stage": current_stage,
#         "evolution": evolution_msg,
#         "xp_gained": xp_gained,
#         "badges_earned": badges_earned,
#         "streak": streak,
#         "streak_rewards": streak_rewards,
#         "message_rewards": message_rewards,
#         "confidence": stage_result.get("confidence", 0),
#         "reason": stage_result.get("reason", "")
#     }

#     if stage_result.get("secondary") and stage_result["confidence"] < 0.7:
#         response_data["note"] = f"I also detected elements of {stage_result['secondary']} stage"

#     return jsonify(response_data)
from flask import Blueprint, request, jsonify
import json
import os
import traceback
from datetime import datetime
from collections import defaultdict
import requests

# Import your project modules - adjust import paths as necessary
from tasks import generate_daily_task, save_completed_task, get_user_tasks
from rewards import get_user_progress, save_user_progress, update_streak, check_streak_rewards, check_message_rewards
from spiral_dynamics import detect_intent, classify_stage, check_evolution, generate_reflective_question, generate_gamified_prompt
from firebase_utils import db
from notifications import send_welcome_notification
from openai import OpenAI  # Your AI client instance configured elsewhere
from spiral_dynamics import client  # Your OpenAI client instance
bp = Blueprint('main', __name__)

AUDIO_FOLDER = "audios"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

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
        if user_id:
            streak = update_streak(user_id)
            rewards = check_streak_rewards(user_id,streak)
            message_rewards = check_message_rewards(user_id)
        intent = detect_intent(entry)
        if intent == "chat":
            prompt_msg = entry
            if reply_to:
                prompt_msg = f"Previous: {reply_to}\nUser: {entry}"
            ai_resp = client.chat.completions.create(
                model='provider-3/gpt-4',
                messages=[{"role": "user", "content": f"Be a kind friend and casually respond to:\n{prompt_msg}"}],
                temperature=0.7,
            ).choices[0].message.content.strip()
            return jsonify({
                "mode": "chat",
                "response": ai_resp,
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
            })
        classification = classify_stage(entry)
        stage = classification.get("stage")
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
        gamified = generate_gamified_prompt(stage or last_stage, entry, evolution=bool(evolution_msg))
        question = generate_reflective_question(entry, reply_to)
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
        if user_id:
            streak = update_streak(user_id)
            rewards = check_streak_rewards(user_id, streak)
            message_rewards = check_message_rewards(user_id)
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
        transcript_text = poll_data.get("text", "")
        utterances = poll_data.get("utterances", [])
        dialogue = "\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in utterances)
        intent = detect_intent(transcript_text)
        if intent == "chat":
            ai_resp = client.chat.completions.create(
                model='provider-3/gpt-4',
                messages=[{"role": "user", "content": f"Carefully respond to:\n{dialogue}"}],
                temperature=0.7,
            ).choices[0].message.content.strip()
            return jsonify({
                "mode": "chat",
                "response": ai_resp,
                "transcription": dialogue,
                "diarized": True,
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
            })
        speaker_texts = defaultdict(str)
        for u in utterances:
            speaker_name = f"Speaker {u['speaker']}"
            speaker_texts[speaker_name] += u["text"] + " "
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
        })
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to process transcription"}), 500


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
        gamified = generate_gamified_prompt(current_stage, text, evolution=bool(evolution_msg))
        question = generate_reflective_question(text, reply_to)
        response_text = f"{evolution_msg}\n\n{question}\n\n{gamified['gamified_prompt']}" if evolution_msg else f"{question}\n\n{gamified['gamified_prompt']}"
        return jsonify({
            "stage": current_stage,
            "question": question,
            "evolution": evolution_msg,
            "gamified": gamified,
            "xp_gain": xp_gain,
            "badges": badges,
        })
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to finalize stage"}), 500