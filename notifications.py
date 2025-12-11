
# from flask import Blueprint, request, jsonify
# from datetime import datetime, timezone
# import traceback
# import hashlib
# from firebase_admin import messaging
# from firebase_utils import db  # Your Firestore client instance
# from tasks import generate_daily_task  # Adjust path as needed

# bp = Blueprint('notifications', __name__)

# # You need to define and manage these globally or in app context appropriately
# NOTIFICATION_TIME = "19:30"  # example initial notification time placeholder
# scheduler = None  # reference to your APScheduler instance
# def schedule_notifications():
#     # Implement your scheduler job registration here
#     pass

# @bp.route('/set_notification_time', methods=['POST'])
# def set_notification_time():
#     global NOTIFICATION_TIME
#     try:
#         data = request.get_json()
#         new_time = data.get('time')
#         # Validate time format HH:MM
#         try:
#             hour, minute = map(int, new_time.split(':'))
#             if not (0 <= hour <= 23 and 0 <= minute <= 59):
#                 raise ValueError
#         except Exception:
#             return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400

#         NOTIFICATION_TIME = new_time
#         if scheduler:
#             try:
#                 scheduler.remove_job("daily_task")
#             except Exception:
#                 pass
#             schedule_notifications()
#         return jsonify({'status': 'success', 'new_time': NOTIFICATION_TIME})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @bp.route('/send_welcome', methods=['POST'])
# def send_welcome():
#     try:
#         data = request.get_json()
#         user_id = data.get('user_id')
#         fcm_token = data.get('fcm_token')
#         if not user_id or not fcm_token:
#             return jsonify({'error': 'Missing user_id or fcm_token'}), 400

#         response = send_welcome_notification(fcm_token)

#         db.collection('users').document(user_id).collection('mergedMessages').add({
#             'type': 'welcome',
#             'message': 'What’s on your mind right now? Write or speak freely—no filters.',
#             'timestamp': datetime.now(timezone.utc),
#             'from': 'system',
#             'is_notification': True
#         })

#         return jsonify({'status': 'success', 'message': 'Welcome notification sent'})
#     except Exception:
#         traceback.print_exc()
#         return jsonify({'error': 'Failed to send welcome notification'}), 500

# def send_welcome_notification(token):
#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title='Welcome to Spiral Dynamics',
#                 body='What’s on your mind right now? Write or speak freely—no filters.'
#             ),
#             token=token,
#         )
#         response = messaging.send(message)
#         return response
#     except Exception as e:
#         print(f'Error sending welcome notification: {e}')
#         return None

# def send_daily_task_notification(fcm_token, task_text):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()
#         notification_id = hashlib.md5(f"{today}_{task_text}".encode()).hexdigest()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 Your Daily Spiral Task",
#                 body=task_text
#             ),
#             data={
#                 "type": "daily_task",
#                 "task": task_text,
#                 "screen": "chat",
#                 "notification_id": notification_id
#             },
#             token=fcm_token,
#             android=messaging.AndroidConfig(collapse_key=notification_id),
#             apns=messaging.APNSConfig(headers={"apns-collapse-id": notification_id})
#         )

#         response = messaging.send(message)
#         return response
#     except Exception as e:
#         print(f"Error sending notification: {e}")
#         return None

# def has_received_today(user_id):
#     today = datetime.now(timezone.utc).date().isoformat()
#     messages_ref = db.collection('users').document(user_id).collection('mergedMessages')
#     query = messages_ref.where('is_notification', '==', True).where('date', '==', today).limit(1)
#     docs = query.stream()
#     return any(True for _ in docs)

# def send_daily_task_to_all():
#     try:
#         task_data = generate_daily_task()
#         task_text = task_data['task']
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 Your Daily Spiral Task",
#                 body=task_text
#             ),
#             data={
#                 "type": "daily_task",
#                 "task": task_text,
#                 "screen": "chat"
#             },
#             topic="daily_task"
#         )
#         response = messaging.send(message)
#         print(f"✅ Topic notification sent: {response}")

#         users_ref = db.collection('users')
#         batch = db.batch()
#         for user_doc in users_ref.stream():
#             user_id = user_doc.id
#             if has_received_today(user_id):
#                 continue
#             notification_ref = db.collection('users').document(user_id).collection('mergedMessages').document()
#             batch.set(notification_ref, {
#                 'type': 'daily_task',
#                 'message': task_text,
#                 'timestamp': datetime.now(timezone.utc),
#                 'from': 'system',
#                 'is_notification': True,
#                 'date': today
#             })
#         batch.commit()
#     except Exception as e:
#         print(f"Error in sending daily task notifications: {e}")

# def send_all_daily_tasks():
#     try:
#         # Generate or fetch today's shared task
#         task_data = generate_daily_task()
#         task_text = task_data["task"]
#         today = datetime.now(timezone.utc).date().isoformat()

#         # ✅ Send one message to the topic
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 Your Daily Spiral Task",
#                 body=task_text
#             ),
#             data={
#                 "type": "daily_task",
#                 "task": task_text,
#                 "screen": "chat"
#             },
#             topic="daily_task"
#         )

#         response = messaging.send(message)
#         print(f"✅ Topic notification sent: {response}")

#         # ✅ Log one bot-message per user in Firestore
#         users_ref = db.collection("users")
#         batch = db.batch()
#         for user_doc in users_ref.stream():
#             user_id = user_doc.id
#             if has_received_today(user_id):
#                 continue
#             notification_ref = db.collection("users").document(user_id)\
#                 .collection("mergedMessages").document()
#             batch.set(notification_ref, {
#                 "type": "daily_task",
#                 "message": task_text,
#                 "timestamp": datetime.now(timezone.utc),
#                 "from": "system",
#                 "is_notification": True,
#                 "date": today
#             })
#         batch.commit()

#     except Exception as e:
#         print(f"Error in send_all_daily_tasks: {e}")

# notifications.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
import traceback
import hashlib
from firebase_admin import messaging
from firebase_utils import db, save_system_merged_message  # helper added to firebase_utils.py
# NOTE: we intentionally DO NOT import generate_daily_task or daily task senders anymore.

bp = Blueprint('notifications', __name__)

# --------- Helpers for Firestore & FCM ---------
def _send_fcm_to_token(token: str, title: str, body: str, data: dict = None):
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
            data=data or {}
        )
        resp = messaging.send(message)
        return resp
    except Exception as e:
        current_app.logger.exception("FCM send failed: %s", e)
        return None


# --------- Intention & Reflection flows ---------
def _today_iso():
    return datetime.now(timezone.utc).date().isoformat()


def get_intention_for_user(user_id: str, day: str = None):
    """Read intention from Firestore path: intentions/{user_id}/days/{date}"""
    try:
        if day is None:
            day = _today_iso()
        doc = db.collection("intentions").document(str(user_id)).collection("days").document(day).get()
        if doc and doc.exists:
            return doc.to_dict().get("intention")
        return None
    except Exception as e:
        current_app.logger.exception("get_intention_for_user failed: %s", e)
        return None


def save_intention_for_user(user_id: str, intention_text: str, day: str = None):
    try:
        if day is None:
            day = _today_iso()
        ref = db.collection("intentions").document(str(user_id)).collection("days").document(day)
        payload = {"intention": intention_text, "created_at": datetime.now(timezone.utc)}
        ref.set(payload, merge=True)
        return True
    except Exception as e:
        current_app.logger.exception("save_intention_for_user failed: %s", e)
        return False


def save_reflection_for_user(user_id: str, rating: int = None, emotion_followup: str = None, day: str = None):
    try:
        if day is None:
            day = _today_iso()
        ref = db.collection("intentions").document(str(user_id)).collection("days").document(day)
        payload = {
            "reflection": {
                "intention_rating": rating,
                "emotion_followup": emotion_followup,
                "reflection_ts": datetime.now(timezone.utc)
            }
        }
        ref.set(payload, merge=True)
        return True
    except Exception as e:
        current_app.logger.exception("save_reflection_for_user failed: %s", e)
        return False


def send_morning_intention_prompt(user_id: str, fcm_token: str = None):
    """
    Sends a system message and optional FCM to prompt the user to set/touch their intention.
    Writes the same mergedMessages structure your UI expects so it appears in-app.
    """
    try:
        today = _today_iso()
        existing = get_intention_for_user(user_id, today)
        if existing:
            title = "Your intention for today"
            body = f"You're aiming for: {existing}. Tap to edit or keep it."
            data = {"type": "morning_intention", "intention": existing}
        else:
            title = "Set today's intention"
            body = "Tap to choose today's intention: Patience · Courage · Calmness · Self-Love"
            data = {"type": "morning_intention", "intention": ""}

        # save system message to mergedMessages so the UI sees it
        save_system_merged_message(user_id, {
            "type": "morning_intention",
            "message": body,
            "timestamp": datetime.now(timezone.utc),
            "from": "system",
            "is_notification": True,
            "date": today
        })

        # send FCM if token present
        if fcm_token:
            _send_fcm_to_token(fcm_token, title, body, data=data)
        return True
    except Exception:
        traceback.print_exc()
        return False


def send_night_reflection_prompt(user_id: str, fcm_token: str = None):
    """
    Sends a night reflection prompt. If user had set an intention, include it and ask for rating.
    """
    try:
        today = _today_iso()
        existing = get_intention_for_user(user_id, today)
        if existing:
            title = "Night reflection"
            body = f"How did your intention '{existing}' hold today? Tap to rate and reflect."
            data = {"type": "night_reflection", "had_intention": "1", "intention": existing}
        else:
            title = "Night reflection"
            body = "How did your day go? Tap to reflect and get a short insight."
            data = {"type": "night_reflection", "had_intention": "0", "intention": ""}

        save_system_merged_message(user_id, {
            "type": "night_reflection",
            "message": body,
            "timestamp": datetime.now(timezone.utc),
            "from": "system",
            "is_notification": True,
            "date": today
        })

        if fcm_token:
            _send_fcm_to_token(fcm_token, title, body, data=data)
        return True
    except Exception:
        traceback.print_exc()
        return False


# --------- API endpoints for Intention flows (register this blueprint) ---------
@bp.route("/intention/set", methods=["POST"])
def api_set_intention():
    try:
        payload = request.get_json() or {}
        user_id = payload.get("user_id")
        intention = payload.get("intention")
        if not user_id or not intention:
            return jsonify({"ok": False, "error": "user_id and intention required"}), 400
        ok = save_intention_for_user(user_id, intention)
        if ok:
            # also add a persisted mergedMessages entry so it shows in user's inbox as a confirmation
            save_system_merged_message(user_id, {
                "type": "intention_set",
                "message": f"Saved intention: {intention}",
                "timestamp": datetime.now(timezone.utc),
                "from": "system",
                "is_notification": False,
                "date": datetime.now(timezone.utc).date().isoformat()
            })
            return jsonify({"ok": True, "intention": intention})
        return jsonify({"ok": False, "error": "failed to save intention"}), 500
    except Exception:
        traceback.print_exc()
        return jsonify({"ok": False, "error": "server error"}), 500


@bp.route("/intention/get/<user_id>", methods=["GET"])
def api_get_intention(user_id):
    try:
        today = _today_iso()
        intention = get_intention_for_user(user_id, today)
        return jsonify({"ok": True, "intention": intention})
    except Exception:
        traceback.print_exc()
        return jsonify({"ok": False, "error": "server error"}), 500


@bp.route("/reflection/submit", methods=["POST"])
def api_submit_reflection():
    """
    Expected JSON: { user_id, rating (int 1-5 optional), emotion_followup (str optional) }
    Saves reflection and generates a short insight message saved into mergedMessages.
    """
    try:
        payload = request.get_json() or {}
        user_id = payload.get("user_id")
        rating = payload.get("rating")
        emotion_followup = payload.get("emotion_followup")
        if not user_id:
            return jsonify({"ok": False, "error": "user_id required"}), 400

        day = _today_iso()
        save_reflection_for_user(user_id, rating=rating, emotion_followup=emotion_followup, day=day)

        # Generate a simple insight (replace with richer logic later)
        intention = get_intention_for_user(user_id, day)
        if intention:
            if rating is None:
                insight = f"You set '{intention}' today. Try rating it nightly to get personalized insights."
            elif int(rating) >= 4:
                insight = f"Nice — your intention '{intention}' held well. Keep building on it."
            elif int(rating) == 3:
                insight = f"Your intention '{intention}' helped somewhat. Small adjustments tomorrow could help."
            else:
                insight = f"'{intention}' wasn't present much today. Try a gentler intention such as Calmness tomorrow."
        else:
            insight = "No intention was set today. Consider setting one tomorrow to give your day more focus."

        if emotion_followup:
            insight += f" Noted emotion: {emotion_followup}."

        # save insight as a system message in mergedMessages
        save_system_merged_message(user_id, {
            "type": "night_insight",
            "message": insight,
            "timestamp": datetime.now(timezone.utc),
            "from": "system",
            "is_notification": False,
            "date": day
        })

        return jsonify({"ok": True, "insight": insight})
    except Exception:
        traceback.print_exc()
        return jsonify({"ok": False, "error": "server error"}), 500
