
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
    build_mission_feedback_line,
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

        # 🔹 NEW: mission completion flag for this specific message
        mission_completed_now = False

        # 🔹 NEW: load basic progress info (for stage logic)
        user_progress = None
        has_stage = False
        quick_stage_mode = False

        if user_id:
            try:
                user_progress = get_user_progress(user_id)
                has_stage = bool(
                    user_progress.get("assessed_stage") or
                    user_progress.get("_last_detected_stage")
                )
                quick_stage_mode = bool(user_progress.get("quick_stage_mode"))
            except Exception as e:
                print("⚠ Could not load user_progress for stage logic:", e)

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

                    # 🔹 mark that user just completed a mission (for chat follow-up)
                    progress["just_completed_mission"] = True

                    save_user_progress(user_id, progress)

                    # 🔹 NEW: this specific message counted as mission completion
                    mission_completed_now = True

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

        # 🔹 if we are in quick stage mode, force spiral (not chat)
        if user_id and quick_stage_mode:
            intent = "spiral"

        # 🔹 ask_stage → simple question
        if intent == "ask_stage" and user_id and (not has_stage) and (not quick_stage_mode):
            question_text = (
                "Love that you’re exploring your Spiral Dynamics level 💫 "
                "It shows you really care about understanding yourself.\n\n"
                "We can start with a simple first snapshot of your stage.\n"
                "For that, share one thing:\n"
                "these days, what feels most important in your life — feeling secure, "
                "achieving your goals, or having close and caring relationships? "
                "Say it in your own words, just like you’d tell a friend."
            )

            try:
                if user_progress is None:
                    user_progress = get_user_progress(user_id)
                user_progress["quick_stage_mode"] = True
                save_user_progress(user_id, user_progress)
            except Exception as e:
                print("⚠ Could not save quick_stage_mode flag:", e)

            base_url = request.url_root.rstrip("/")
            audio_url = f"{base_url}/speak-stream?text={quote_plus(question_text)}"

            if user_id:
                try:
                    save_conversation_message(user_id, "assistant", question_text)
                except Exception as e:
                    print("⚠ Could not save stage question message:", e)

            return jsonify({
                "mode": "chat",
                "response": question_text,
                "audiourl": audio_url,
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
                "missions_completed": missions_completed,
                "new_mission_reward": new_mission_reward,
                "stage_assessment": True,
            })

        # ---------------- CHAT FLOW ----------------
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

            # B-type follow-up after mission completion (text + voice mode)
            if user_id:
                try:
                    progress = get_user_progress(user_id)
                    if progress.get("just_completed_mission"):
                        followup = (
                            "\n\nI’m really glad you showed up for yourself today. "
                            "If it feels right, we can stay with this feeling a bit more — "
                            "or you can talk about anything else that’s on your mind."
                        )
                        ai_resp = ai_resp + followup
                        progress["just_completed_mission"] = False
                        save_user_progress(user_id, progress)
                except Exception as e:
                    print("⚠ mission follow-up blend failed:", e)

            # 🔊 TTS URL only for this response
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
                "audiourl": audio_url,
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
                "missions_completed": missions_completed,
                "new_mission_reward": new_mission_reward,
            })

        # ---------------------------
        # Spiral (reflection) flow
        # ---------------------------
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

        # 🔹 NEW: mission feedback line (stage + mood + completion)
        mission_feedback = ""
        if mission_completed_now:
            mission_feedback = build_mission_feedback_line(
                stage,
                classification.get("mood"),
                completion="full",
            )

        # quick-stage answer → save assessed_stage
        if user_id and quick_stage_mode and stage:
            try:
                progress = get_user_progress(user_id)
                progress["assessed_stage"] = stage
                progress["assessed_stage_confidence"] = classification.get("confidence")
                if classification.get("secondary"):
                    progress["assessed_stage_secondary"] = classification.get("secondary")
                progress["quick_stage_mode"] = False
                save_user_progress(user_id, progress)
            except Exception as e:
                print("⚠ Could not save assessed_stage from quick assessment:", e)

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
                mm = mind_mirror_gen
                prev_mind = None
                prev_mission = None
                if not mm:
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

        # 🔊 Spiral reply TTS
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
        # 🔹 NEW: speak mission feedback if present
        if mission_feedback:
            tts_parts.append(mission_feedback)

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
        # 🔹 NEW: add mission_feedback as separate field (format break होत नाही, फक्त extra key)
        if mission_feedback:
            response["mission_feedback"] = mission_feedback

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

        # 🔹 NEW: mission completion flag for this audio message
        mission_completed_now = False

        if user_id:
            streak = update_streak(user_id)
            rewards = check_streak_rewards(user_id, streak)
            message_rewards = check_message_rewards(user_id)

        # 🔹 NEW: load quick stage flags for voice
        user_progress = None
        has_stage = False
        quick_stage_mode = False
        if user_id:
            try:
                user_progress = get_user_progress(user_id)
                has_stage = bool(
                    user_progress.get("assessed_stage") or
                    user_progress.get("_last_detected_stage")
                )
                quick_stage_mode = bool(user_progress.get("quick_stage_mode"))
            except Exception as e:
                print("⚠ Could not load user_progress for stage (audio):", e)

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

                    progress = get_user_progress(user_id)
                    progress["missions_completed"] = progress.get("missions_completed", 0) + 1
                    missions_completed = progress["missions_completed"]

                    if missions_completed in MISSION_REWARDS:
                        reward = MISSION_REWARDS[missions_completed]
                        progress["xp"] += reward["xp"]
                        if reward["badge"] not in progress.get("badges", []):
                            progress["badges"].append(reward["badge"])
                        new_mission_reward = reward

                    # mark mission completion for voice flow
                    progress["just_completed_mission"] = True
                    save_user_progress(user_id, progress)

                    # 🔹 NEW: this specific audio message counted as mission completion
                    mission_completed_now = True

            except Exception as e:
                print("⚠ Error marking growth prompt complete (audio):", e)

        # 🔊 save audio locally
        filename = f"{user_id or 'anon'}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.wav"
        os.makedirs("audios", exist_ok=True)
        path = os.path.join("audios", filename)
        audio_file.save(path)

        # 👉 TRANSCRIBE WITH OPENAI WHISPER
        try:
            with open(path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=f,
                )
            transcript_text = getattr(transcript, "text", "") or (
                transcript.get("text", "") if isinstance(transcript, dict) else ""
            )
            transcript_text = (transcript_text or "").strip()
        except Exception as e:
            print("⚠ Whisper transcription failed:", e)
            return jsonify({"error": "Transcription failed"}), 500

        # ---------------- INTENT ----------------
        intent = detect_intent(transcript_text)

        # ask_stage for voice when no stage yet
        if intent == "ask_stage" and user_id and (not has_stage) and (not quick_stage_mode):
            question_text = (
                "Love that you’re exploring your Spiral Dynamics level 💫 "
                "It shows you really care about understanding yourself.\n\n"
                "We can start with a simple first snapshot of your stage.\n"
                "For that, share one thing:\n"
                "these days, what feels most important in your life — feeling secure, "
                "achieving your goals, or having close and caring relationships? "
                "Say it in your own words, just like you’d tell a friend."
            )

            try:
                if user_progress is None:
                    user_progress = get_user_progress(user_id)
                user_progress["quick_stage_mode"] = True
                save_user_progress(user_id, user_progress)
            except Exception as e:
                print("⚠ Could not save quick_stage_mode flag (audio):", e)

            base_url = request.url_root.rstrip("/")
            audio_url = f"{base_url}/speak-stream?text={quote_plus(question_text)}"

            return jsonify({
                "mode": "chat",
                "response": question_text,
                "audiourl": audio_url,
                "transcription": transcript_text,
                "diarized": False,
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
                "missions_completed": missions_completed,
                "new_mission_reward": new_mission_reward,
                "stage_assessment": True,
            })

        # if we are in quick stage mode, force spiral path
        if user_id and quick_stage_mode:
            intent = "spiral"

        # -------------- CHAT FLOW --------------
        if intent == "chat":
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a warm, supportive friend in the RETVRN app. "
                        "Reply in simple, natural language, 2–4 short sentences. "
                        "No roleplay—just a normal, human reply."
                    ),
                },
                {
                    "role": "user",
                    "content": transcript_text,
                },
            ]

            ai_resp = client.chat.completions.create(
                model='gpt-4.1',
                messages=messages,
                temperature=0.7,
            ).choices[0].message.content.strip()

            # B-type follow-up after mission completion (voice input)
            if user_id:
                try:
                    progress = get_user_progress(user_id)
                    if progress.get("just_completed_mission"):
                        followup = (
                            "\n\nI’m really glad you showed up for yourself today. "
                            "If it feels right, we can stay with this feeling a bit more — "
                            "or you can talk about anything else that’s on your mind."
                        )
                        ai_resp = ai_resp + followup
                        progress["just_completed_mission"] = False
                        save_user_progress(user_id, progress)
                except Exception as e:
                    print("⚠ mission follow-up blend failed (audio):", e)

            base_url = request.url_root.rstrip("/")
            tts_text = ai_resp
            audio_url = f"{base_url}/speak-stream?text={quote_plus(tts_text)}"

            return jsonify({
                "mode": "chat",
                "response": ai_resp,
                "audiourl": audio_url,
                "transcription": transcript_text,
                "diarized": False,
                "streak": streak,
                "rewards": rewards,
                "message_rewards": message_rewards,
                "missions_completed": missions_completed,
                "new_mission_reward": new_mission_reward,
            })

        # -------------- SPIRAL FLOW (single speaker) --------------
        try:
            classification = classify_stage(transcript_text)
        except TypeError:
            classification = classify_stage(transcript_text)

        stage = classification.get("stage")
        evolution_msg = check_evolution(last_stage, classification)

        # 🔹 NEW: mission feedback for voice spiral
        mission_feedback = ""
        if mission_completed_now:
            mission_feedback = build_mission_feedback_line(
                stage,
                classification.get("mood"),
                completion="full",
            )

        # quick-stage answer → save assessed_stage once (voice)
        if user_id and quick_stage_mode and stage:
            try:
                progress = get_user_progress(user_id)
                progress["assessed_stage"] = stage
                progress["assessed_stage_confidence"] = classification.get("confidence")
                if classification.get("secondary"):
                    progress["assessed_stage_secondary"] = classification.get("secondary")
                progress["quick_stage_mode"] = False
                save_user_progress(user_id, progress)
            except Exception as e:
                print("⚠ Could not save assessed_stage from quick assessment (audio):", e)

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

        gamified = generate_gamified_prompt(
            stage or last_stage,
            transcript_text,
            evolution=bool(evolution_msg),
        )

        try:
            question = generate_reflective_question(
                transcript_text,
                reply_to=reply_to or None,
            )
        except TypeError:
            question = generate_reflective_question(transcript_text, reply_to)

        # NOTE: इथे TTS text full spiral साठी नाही add केलं (तुला हवं असेल तर इथेही tts_parts + audiourl जसं merged मध्ये तसं करू शकतो)

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
            "transcription": transcript_text,
            "diarized": False,
            "ask_speaker_pick": False,
            "streak": streak,
            "rewards": rewards,
            "message_rewards": message_rewards,
            "missions_completed": missions_completed,
            "new_mission_reward": new_mission_reward,
        }
        if mission_feedback:
            response["mission_feedback"] = mission_feedback

        return jsonify(response)

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