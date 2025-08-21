import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import traceback
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import random
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, messaging, firestore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
# ✅ Import A4F-compatible OpenAI SDK
from openai import OpenAI
from datetime import datetime, timezone
import hashlib


# Load environment variables
load_dotenv()
a4f_api_key = os.getenv("A4F_API_KEY")
assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")


# Firebase configuration from environment variables
FIREBASE_CONFIG = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")  # Added with default
}


if not a4f_api_key or not assemblyai_api_key:
    raise ValueError("❌ Missing A4F or AssemblyAI API key in .env")

try:
    cred = credentials.Certificate(FIREBASE_CONFIG)
    firebase_admin.initialize_app(cred)
    
    # scheduler.start()
    
    FIREBASE_INITIALIZED = True
    db = firestore.client()
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    FIREBASE_INITIALIZED = False

# ✅ Initialize A4F OpenAI client
client = OpenAI(
    api_key=a4f_api_key,
    base_url="https://api.a4f.co/v1"
)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Initialize scheduler
scheduler = BackgroundScheduler(daemon=True)
# scheduler.start()

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "Backend is running!"

STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]
COMPLETED_TASKS_FILE = "completed_tasks.json"
DAILY_TASKS_FILE = "daily_tasks.json"
AUDIO_FOLDER = "static/audio"
USER_PROGRESS_FILE = "user_progress.json"
NOTIFICATION_TIME = os.getenv("NOTIFICATION_TIME", "09:00")  # Default to 9:00 AM

os.makedirs(AUDIO_FOLDER, exist_ok=True)

# XP and Badges Configuration
XP_REWARDS = {
    "level_up": 10,
    "daily_streak_3": 15,
    "daily_streak_7": 30,
    "daily_streak_14": 50,
    "daily_streak_30": 100,
    "message_streak_5": 20
}

BADGES = {
    "level_up": "🌱 Level Up",
    "daily_streak_3": "🔥 3-Day Streak",
    "daily_streak_7": "🌟 Weekly Explorer",
    "daily_streak_14": "🌙 Fortnight Champion",
    "daily_streak_30": "🌕 Monthly Master",
    "message_streak_5": "💬 Chatterbox"
}

SPIRAL_TASKS = [
    "Recall a time when your only focus was to make it through the day. What mattered most in that moment?",
    "When your basic needs aren't met, how does your mindset change?",
    "Think of a moment when safety or food felt uncertain. How did you respond?",
    "Are there superstitions or rituals you follow without fully knowing why? What do they mean to you?",
    "Describe a tradition your family follows that makes you feel rooted. Why is it important?",
    "How do you stay connected to your ancestry, roots, or community?",
    "Have you ever acted on impulse just because it felt right in the moment? What happened?",
    "Describe a time when you took control of a situation without waiting for permission. Why did you do it?",
    "When do you feel most powerful or in control?",
    "How do you deal with people who challenge your authority or choices?",
    "What moral code or set of values do you try to live by? How did you come to believe in it?",
    "Think of a time you followed a rule that you didn't fully agree with. Why did you do it?",
    "What does loyalty mean to you, and who deserves it?",
    "When someone breaks a rule or law, what's your first reaction — curiosity, anger, or something else?",
    "What does success mean to you beyond financial gain? How do you measure your progress?",
    "Have you ever pushed yourself too hard to prove something to others? Why did it matter so much?",
    "How do you react when someone limits your freedom or questions your ability?",
    "What's a personal goal that you're proud of achieving? What drove you to it?",
    "Is competition a healthy part of life for you? Why or why not?",
    "When was the last time you deeply empathized with someone you disagreed with? What did you learn?",
    "How do you decide when to speak up for others versus stay quiet for harmony?",
    "Think of a group or cause you care about. Why does it matter to you?",
    "Do you believe in absolute truths, or is everything relative to context?",
    "How do you handle tension when people don't feel heard?",
    "Do you ever hide your opinions to keep peace? How does that affect you?",
    "Have you ever realized both sides of an argument were valid? How did you respond?",
    "Do you ever switch perspectives just to understand something more deeply?",
    "Describe a moment when you helped two opposing views find common ground.",
    "What's more important to you — being right, or being helpful in a larger system?",
    "How do you handle paradoxes or contradictions in life?",
    "Have you ever felt part of something much larger than yourself? What was that experience like?",
    "How do you define harmony — is it internal, collective, spiritual?",
    "When do you feel most connected to all forms of life or nature?",
    "Describe a time you made a decision that honored both logic and intuition.",
    "What does planetary well-being mean to you?",
    "Have your values changed over the years? What sparked the shift?",
    "When do you feel most authentic — when leading, listening, creating, or something else?",
    "What role does tradition play in your life today?",
    "When you disagree with someone close to you, do you debate, reflect, or avoid?",
    "What part of your identity do you feel is constantly evolving?",
    "Do you feel you have a personal truth? How did you discover it?",
    "How do you know when it's time to move on from a belief?",
    "If someone asked why you do what you do, how would you explain your purpose?",
    "When you're uncertain, what guides your choices — logic, values, instinct, or something else?",
    "What does freedom mean to you right now?",
    "Have you ever tried to influence others' beliefs? Why or why not?",
    "Do you often seek answers, or feel okay with not knowing?",
    "Do you adapt your behavior depending on the environment or people around you?",
    "When was the last time you questioned your worldview?",
    "If everyone followed your philosophy of life, what kind of world would we have?",
    "Do you trust people easily? Why or why not?",
    "What do you feel you've outgrown, mentally or emotionally?",
    "Do you often feel pulled in different directions — between structure, freedom, purpose, and peace?",
    "Do you value clarity or complexity more when making sense of life?",
    "What type of change feels threatening to you, and why?",
    "What type of change feels exciting to you, and why?",
    "How do you decide what's worth standing up for?",
    "What kind of legacy feels meaningful to leave behind?",
    "What does growth mean to you?",
    "If you could fully express your truth without fear, what would you say?"
]

STAGE_GAMIFIED_META = {
    "Beige": {
        "emoji": "🏕",
        "name": "Survival Basecamp",
        "reward": "+5 XP (🌱 Survivalist)"
    },
    "Purple": {
        "emoji": "🪄",
        "name": "Tribe Mystic",
        "reward": "+10 XP (🧙 Tribal Keeper)"
    },
    "Red": {
        "emoji": "🔥",
        "name": "Dragon's Lair",
        "reward": "+15 XP (🐉 Force Master)"
    },
    "Blue": {
        "emoji": "📜",
        "name": "Order Temple",
        "reward": "+20 XP (🛡 Virtue Guardian)"
    },
    "Orange": {
        "emoji": "🚀",
        "name": "Achiever's Arena",
        "reward": "+25 XP (🏆 Success Champion)"
    },
    "Green": {
        "emoji": "🌀",
        "name": "Harmony Nexus",
        "reward": "+30 XP (🌍 Community Builder)"
    },
    "Yellow": {
        "emoji": "🔄",
        "name": "Flow Integrator",
        "reward": "+35 XP (🌀 Complexity Dancer)"
    },
    "Turquoise": {
        "emoji": "🌌",
        "name": "Cosmic Weave",
        "reward": "+40 XP (♾ Holon Seer)"
    }
}

def init_task_files():
    for file_path in [COMPLETED_TASKS_FILE, DAILY_TASKS_FILE, USER_PROGRESS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                if file_path == USER_PROGRESS_FILE:
                    json.dump({}, f)
                else:
                    json.dump([], f)

init_task_files()


# Notification functions

def send_daily_task_notification(fcm_token, task_text):
    try:
        # Create a unique ID based on the task text and date
        today = datetime.now(timezone.utc).date().isoformat()
        notification_id = hashlib.md5(f"{today}_{task_text}".encode()).hexdigest()
        
        message = messaging.Message(
            notification=messaging.Notification(
                title="🌱 Your Daily Spiral Task",
                body=task_text
            ),
            data={
                "type": "daily_task",
                "task": task_text,
                "screen": "chat",
                "notification_id": notification_id  # Add this line
            },
            token=fcm_token,
            android=messaging.AndroidConfig(
                collapse_key=notification_id  # Use same ID for collapse
            ),
            apns=messaging.APNSConfig(
                headers={
                    "apns-collapse-id": notification_id  # iOS equivalent
                }
            )
        )
        
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Error sending notification: {e}")
        return None

def has_received_today(user_id):
    today = datetime.now(timezone.utc).date().isoformat()
    messages_ref = db.collection("users").document(user_id)\
        .collection("mergedMessages")
    
    query = messages_ref\
        .where("is_notification", "==", True)\
        .where("date", "==", today)\
        .limit(1)
    
    docs = query.stream()
    return any(True for _ in docs)  # Returns True if any docs exist


def send_all_daily_tasks():
    try:
        # Generate or fetch today's shared task
        task_data = generate_daily_task()
        task_text = task_data["task"]
        today = datetime.now(timezone.utc).date().isoformat()

        # ✅ Send one message to the topic
        message = messaging.Message(
            notification=messaging.Notification(
                title="🌱 Your Daily Spiral Task",
                body=task_text
            ),
            data={
                "type": "daily_task",
                "task": task_text,
                "screen": "chat"
            },
            topic="daily_task"
        )

        response = messaging.send(message)
        print(f"✅ Topic notification sent: {response}")

        # ✅ Log one bot-message per user in Firestore
        users_ref = db.collection("users")
        batch = db.batch()
        for user_doc in users_ref.stream():
            user_id = user_doc.id
            if has_received_today(user_id):
                continue
            notification_ref = db.collection("users").document(user_id)\
                .collection("mergedMessages").document()
            batch.set(notification_ref, {
                "type": "daily_task",
                "message": task_text,
                "timestamp": datetime.now(timezone.utc),
                "from": "system",
                "is_notification": True,
                "date": today
            })
        batch.commit()

    except Exception as e:
        print(f"Error in send_all_daily_tasks: {e}")



def schedule_daily_notifications():
    """Schedule daily notifications using APScheduler"""
    try:
        hour, minute = map(int, NOTIFICATION_TIME.split(':'))
        trigger = CronTrigger(hour=hour, minute=minute, timezone="UTC")

        scheduler.add_job(
            func=send_all_daily_tasks,
            trigger=trigger,
            name="daily_task_notification",
            misfire_grace_time=60*60  # 1 hour grace period
        )
        # scheduler.start()
        print(f"⏰ Scheduled daily notifications at {NOTIFICATION_TIME} UTC")
    except Exception as e:
        print(f"⚠ Error scheduling notifications: {e}")



def get_user_progress(user_id):
    try:
        with open(USER_PROGRESS_FILE, "r") as f:
            all_progress = json.load(f)
        return all_progress.get(user_id, {
            "xp": 0,
            "level": 1,
            "last_level": 1,
            "streak": 0,
            "last_active_date": None,
            "message_count": 0,
            "badges": []
        })
    except:
        return {
            "xp": 0,
            "level": 1,
            "last_level": 1,
            "streak": 0,
            "last_active_date": None,
            "message_count": 0,
            "badges": []
        }

def save_user_progress(user_id, progress):
    try:
        with open(USER_PROGRESS_FILE, "r") as f:
            all_progress = json.load(f)
        all_progress[user_id] = progress
        with open(USER_PROGRESS_FILE, "w") as f:
            json.dump(all_progress, f, indent=2)
    except Exception as e:
        print("Error saving user progress:", e)

def update_streak(user_id):
    progress = get_user_progress(user_id)
    today = datetime.utcnow().date().isoformat()
    last_active = progress.get("last_active_date")
    
    if last_active == today:
        return progress["streak"]
    
    if last_active and (datetime.fromisoformat(last_active).date() + timedelta(days=1)) == datetime.utcnow().date():
        progress["streak"] += 1
    else:
        progress["streak"] = 1
    
    progress["last_active_date"] = today
    save_user_progress(user_id, progress)
    return progress["streak"]

def check_streak_rewards(user_id, streak):
    progress = get_user_progress(user_id)
    rewards = []
    
    if streak == 3 and "daily_streak_3" not in progress["badges"]:
        progress["xp"] += XP_REWARDS["daily_streak_3"]
        progress["badges"].append("daily_streak_3")
        rewards.append(BADGES["daily_streak_3"])
    
    if streak == 7 and "daily_streak_7" not in progress["badges"]:
        progress["xp"] += XP_REWARDS["daily_streak_7"]
        progress["badges"].append("daily_streak_7")
        rewards.append(BADGES["daily_streak_7"])
    
    if streak == 14 and "daily_streak_14" not in progress["badges"]:
        progress["xp"] += XP_REWARDS["daily_streak_14"]
        progress["badges"].append("daily_streak_14")
        rewards.append(BADGES["daily_streak_14"])
    
    if streak == 30 and "daily_streak_30" not in progress["badges"]:
        progress["xp"] += XP_REWARDS["daily_streak_30"]
        progress["badges"].append("daily_streak_30")
        rewards.append(BADGES["daily_streak_30"])
    
    if rewards:
        save_user_progress(user_id, progress)
    
    return rewards

def check_message_rewards(user_id):
    progress = get_user_progress(user_id)
    progress["message_count"] += 1
    rewards = []
    
    if progress["message_count"] >= 5 and "message_streak_5" not in progress["badges"]:
        progress["xp"] += XP_REWARDS["message_streak_5"]
        progress["badges"].append("message_streak_5")
        rewards.append(BADGES["message_streak_5"])
    
    save_user_progress(user_id, progress)
    return rewards

def get_user_tasks(user_id, file_path):
    try:
        with open(file_path, "r") as f:
            tasks = json.load(f)
        return [t for t in tasks if t.get("user_id") == user_id]
    except:
        return []

def get_recent_tasks(user_id, n_days=30):
    user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
    cutoff = datetime.utcnow().date() - timedelta(days=n_days)
    return [t['task'] for t in user_tasks if datetime.fromisoformat(t['date']).date() >= cutoff]

def generate_daily_task_content(user_id, recent_tasks):
    available = [task for task in SPIRAL_TASKS if task not in recent_tasks]
    if not available:
        available = SPIRAL_TASKS[:]
    return random.choice(available)

def save_daily_task(task_data):
    try:
        with open(DAILY_TASKS_FILE, "r") as f:
            tasks = json.load(f)
        tasks = [t for t in tasks if not (
            t.get("user_id") == task_data.get("user_id") and 
            t.get("date") == task_data.get("date")
        )]
        tasks.append(task_data)
        with open(DAILY_TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print("Error saving daily task:", e)

def save_completed_task(user_id, task_data):
    try:
        with open(COMPLETED_TASKS_FILE, "r") as f:
            tasks = json.load(f)
        tasks.append({
            "user_id": user_id,
            "task": task_data.get("task"),
            "stage": task_data.get("stage"),
            "date": datetime.utcnow().date().isoformat(),
            "completed": True,
            "timestamp": datetime.utcnow().isoformat(),
            "completion_timestamp": datetime.utcnow().isoformat()
        })
        with open(COMPLETED_TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print("Error saving completed task:", e)
    
#     return task_data
def generate_daily_task():
    """Generate a single daily task for all users"""
    today = datetime.utcnow().date().isoformat()
    
    # Check if a task already exists for today
    try:
        with open(DAILY_TASKS_FILE, "r") as f:
            tasks = json.load(f)
    except:
        tasks = []
    
    # Find any task from today (regardless of user)
    existing_task = next((t for t in tasks if t.get("date") == today), None)
    if existing_task:
        return existing_task
    
    # If no task exists for today, generate a new one
    task_content = random.choice(SPIRAL_TASKS)
    task_data = {
        "user_id": "all",  # Mark this as a task for all users
        "task": task_content,
        "date": today,
        "completed": False,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Save the task
    tasks.append(task_data)
    with open(DAILY_TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)
    
    return task_data
def detect_intent(entry):
    prompt = (
        "You are a Spiral Dynamics gatekeeper.\n"
        "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
        "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
        f"Entry: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="provider-3/gpt-4",  # or "provider-3/gpt-4o"
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return "spiral" if "spiral" in response.choices[0].message.content.lower() else "chat"
def classify_stage(entry):
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
        model="provider-3/gpt-4",
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
    except:
        # Fallback to simple classification if JSON parsing fails
        simple_response = client.chat.completions.create(
            model="provider-3/gpt-4",
            messages=[{"role": "user", "content": f"Classify this into one stage from {', '.join(STAGES)}: {entry}"}],
            temperature=0
        )
        return {
            "stage": simple_response.choices[0].message.content.strip(),
            "secondary": None,
            "confidence": 1.0,
            "reason": ""
        }

def generate_reflective_question(entry, reply_to=None):
    context = f"\nReplying to: \"{reply_to}\"" if reply_to else ""
    prompt = (
        f"You are a Spiral Dynamics mentor. Based on the user's thoughts{context}, "
        f"ask one deep, emotionally resonant question (max 15 words). Just ask the question.\n\n"
        f"User message: \"{entry}\""
    )
    response = client.chat.completions.create(
        model="provider-3/gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
    )
    return response.choices[0].message.content.strip()


def generate_gamified_prompt(stage, entry, evolution=False):
    """Generate dynamic gamified prompts based on stage and evolution status"""
    stage_meta = STAGE_GAMIFIED_META.get(stage, STAGE_GAMIFIED_META["Green"])
    
    # Generate context-aware prompt based on stage and user input
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
        model="provider-3/gpt-4",  # or "provider-3/gpt-4o"
        messages=[{"role": "user", "content": prompt_template}],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    try:
        content = json.loads(response.choices[0].message.content)
        return {
            "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 {content['question']}",
            "gamified_prompt": f"💡 {content['prompt']}",
            "reward": content['reward'] if evolution else stage_meta["reward"]
        }
    except:
        # Fallback if JSON parsing fails
        return {
            "gamified_question": f"{stage_meta['emoji']} {stage_meta['name']}\n🎯 What about this resonates most with you?",
            "gamified_prompt": "💡 Reflect on how this shows up in your daily life",
            "reward": stage_meta["reward"]
        }


def check_evolution(last_stage, current_result):
    """current_result is now the full classification result"""
    if not last_stage:
        return None
        
    current_stage = current_result["stage"]
    try:
        last_index = STAGES.index(last_stage)
        current_index = STAGES.index(current_stage)
        
        if current_index > last_index:
            confidence = current_result.get("confidence", 0)
            if confidence >= 0.6:  # Only announce evolution if confident
                return f"🌱 Level Up! You're showing strong {current_stage} tendencies! (Also some {current_result.get('secondary')})" if current_result.get("secondary") else f"🌱 Level Up! You've evolved to {current_stage} stage! 🌟"
            else:
                return f"🌀 You're exploring {current_stage} (with some {last_stage} still present)"
    except ValueError:
        pass
    return None

@app.route("/daily_task", methods=["GET"])
def get_daily_task():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        
        # Get the shared daily task
        task_data = generate_daily_task()
        
        # Check if this user has completed it
        with open(COMPLETED_TASKS_FILE, "r") as f:
            completed_tasks = json.load(f)
        
        user_completed = any(
            t.get("user_id") == user_id and 
            t.get("date") == task_data.get("date") and 
            t.get("completed")
            for t in completed_tasks
        )
        
        # Add completion status to the response
        response_data = dict(task_data)
        response_data["user_completed"] = user_completed
        
        return jsonify(response_data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
        
@app.route("/complete_task", methods=["POST"])
def complete_task():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        task_id = data.get("task_id")

        if not user_id or not task_id:
            return jsonify({"error": "Missing user_id or task_id"}), 400

        with open(DAILY_TASKS_FILE, "r") as f:
            daily_tasks = json.load(f)

        task_to_complete = None
        for task in daily_tasks:
            if str(task.get("timestamp")) == task_id and task.get("user_id") == user_id:
                task["completed"] = True
                task["completion_timestamp"] = datetime.utcnow().isoformat()
                task_to_complete = task
                break

        if not task_to_complete:
            return jsonify({"error": "Task not found"}), 404

        with open(DAILY_TASKS_FILE, "w") as f:
            json.dump(daily_tasks, f, indent=2)

        save_completed_task(user_id, task_to_complete)
        return jsonify({"message": "Task marked as completed"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/task_history", methods=["GET"])
def get_task_history():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        completed_tasks = get_user_tasks(user_id, COMPLETED_TASKS_FILE)
        return jsonify(completed_tasks)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/user_progress", methods=["GET"])
def get_user_progress_endpoint():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        
        progress = get_user_progress(user_id)
        return jsonify(progress)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/merged", methods=["POST"])
def merged_reflection():
    try:
        data = request.get_json()
        entry = data.get("text", "").strip()
        last_stage = data.get("last_stage", "").strip()
        reply_to = data.get("reply_to", "").strip()
        user_id = data.get("user_id")

        if not entry:
            return jsonify({"error": "Missing journaling input."}), 400

        # Update user activity tracking
        streak = 0
        streak_rewards = []
        message_rewards = []
        if user_id:
            streak = update_streak(user_id)
            streak_rewards = check_streak_rewards(user_id, streak)
            message_rewards = check_message_rewards(user_id)
        
        intent = detect_intent(entry)

        if intent == "chat":
            message = f"User: {reply_to}\n\nUser response: {entry}" if reply_to else entry
            reply = client.chat.completions.create(
                model="provider-3/gpt-4",  # or "provider-3/gpt-4o"
                messages=[{"role": "user", "content": f"You are a kind friend. Respond casually to: {message}"}],
                temperature=0.7,
            ).choices[0].message.content.strip()

            response_data = {
                "mode": "chat",
                "response": reply
            }
            
            if user_id:
                response_data["streak"] = streak
                if streak_rewards:
                    response_data["rewards"] = streak_rewards
                if message_rewards:
                    response_data["message_rewards"] = message_rewards
            
            return jsonify(response_data)

        stage_result = classify_stage(entry)
        current_stage = stage_result["stage"]
        evolution_msg = check_evolution(last_stage, stage_result)
        
        # Handle XP for level up
        xp_gained = 0
        badges_earned = []
        if user_id and evolution_msg:
            progress = get_user_progress(user_id)
            progress["xp"] += XP_REWARDS["level_up"]
            if "level_up" not in progress["badges"]:
                progress["badges"].append("level_up")
                badges_earned.append(BADGES["level_up"])
            xp_gained = XP_REWARDS["level_up"]
            save_user_progress(user_id, progress)
        
        # Generate appropriate response based on evolution status
        if evolution_msg:
            gamified = generate_gamified_prompt(current_stage, entry, evolution=True)
            question = generate_reflective_question(entry, reply_to)
            response_text = f"{evolution_msg}\n\n{question}\n\n{gamified['gamified_prompt']}"
        else:
            gamified = generate_gamified_prompt(last_stage if last_stage else current_stage, entry)
            question = generate_reflective_question(entry, reply_to)
            response_text = f"{question}\n\n{gamified['gamified_prompt']}"

        response_data = {
            "mode": "spiral",
            "stage": current_stage,
            "question": question,
            "evolution": evolution_msg,
            "gamified": gamified,
            "confidence": stage_result["confidence"],
            "reason": stage_result["reason"]
        }

        # Add user progress info if available
        if user_id:
            response_data.update({
                "xp_gained": xp_gained,
                "badges_earned": badges_earned,
                "streak": streak,
                "streak_rewards": streak_rewards,
                "message_rewards": message_rewards
            })

        # Add secondary stage info if present and confidence is low
        if stage_result.get("secondary") and stage_result["confidence"] < 0.7:
            response_data["note"] = f"I also detected elements of {stage_result['secondary']} stage"

        return jsonify(response_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/reflect_transcription", methods=["POST"])
def reflect_transcription():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "Missing audio file"}), 400

        reply_to = request.form.get("reply_to", "").strip()
        last_stage = request.form.get("last_stage", "").strip()
        user_id = request.form.get("user_id")
        audio_file = request.files["audio"]

        # Update user activity tracking
        streak = 0
        streak_rewards = []
        message_rewards = []
        if user_id:
            streak = update_streak(user_id)
            streak_rewards = check_streak_rewards(user_id, streak)
            message_rewards = check_message_rewards(user_id)

        os.makedirs("audios", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filepath = os.path.join("audios", f"{timestamp}.wav")
        audio_file.save(filepath)

        # Upload audio to AssemblyAI
        with open(filepath, "rb") as f:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers={
                    "authorization": assemblyai_api_key,
                    "content-type": "application/octet-stream"
                },
                data=f
            )
        audio_url = upload_response.json()["upload_url"]

        # Request transcription
        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={"authorization": assemblyai_api_key},
            json={
                "audio_url": audio_url,
                "speaker_labels": True
            }
        )
        transcript_id = transcript_response.json()["id"]

        # Poll until transcription is complete
        while True:
            poll = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers={"authorization": assemblyai_api_key}
            )
            result = poll.json()
            if result["status"] in ("completed", "error"):
                break

        if result["status"] == "error":
            return jsonify({"error": "Transcription failed."}), 500

        text = result.get("text", "").strip()
        utterances = result.get("utterances", [])

        speaker_dialogue = "\n".join(
            [f"Speaker {ord(u['speaker'].upper()) - ord('A') + 1}: {u['text']}" for u in utterances]
        )

        intent = detect_intent(text)

        # If intent is chat, respond casually
        if intent == "chat":
            reply = client.chat.completions.create(
                model="provider-3/gpt-4",  # or provider-3/gpt-4o
                messages=[{"role": "user", "content": f"You are a kind friend. Respond casually to this conversation:\n{speaker_dialogue}"}],
                temperature=0.7,
            ).choices[0].message.content.strip()

            response_data = {
                "mode": "chat",
                "response": reply,
                "transcription": speaker_dialogue,
                "diarized": True
            }

            if user_id:
                response_data["streak"] = streak
                if streak_rewards:
                    response_data["rewards"] = streak_rewards
                if message_rewards:
                    response_data["message_rewards"] = message_rewards

            return jsonify(response_data)

        # Otherwise classify each speaker's stage
        speaker_texts = defaultdict(str)
        for u in utterances:
            speaker_id = f"Speaker {ord(u['speaker'].upper()) - ord('A') + 1}"
            speaker_texts[speaker_id] += u['text'].strip() + " "

        speaker_stages = {}
        for speaker, combined_text in speaker_texts.items():
            try:
                stage = classify_stage(combined_text)
                speaker_stages[speaker] = {
                    "stage": stage["stage"],
                    "text": combined_text
                }
            except Exception as e:
                speaker_stages[speaker] = {
                    "stage": "Unknown",
                    "text": combined_text,
                    "error": str(e)
                }

        response_data = {
            "mode": "spiral",
            "transcription": speaker_dialogue,
            "speaker_stages": speaker_stages,
            "diarized": True,
            "ask_speaker_pick": True
        }

        if user_id:
            response_data["streak"] = streak
            if streak_rewards:
                response_data["rewards"] = streak_rewards
            if message_rewards:
                response_data["message_rewards"] = message_rewards

        return jsonify(response_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/finalize_stage", methods=["POST"])
def finalize_stage():
    try:
        data = request.get_json()
        speaker_id = data.get("speaker_id")
        speaker_stages = data.get("speaker_stages", {})
        last_stage = data.get("last_stage", "").strip()
        reply_to = data.get("reply_to", "").strip()
        user_id = data.get("user_id")

        speaker_data = speaker_stages.get(speaker_id)
        if not speaker_data:
            return jsonify({"error": "Speaker not found"}), 400

        current_stage = speaker_data.get("stage", "Unknown")
        text = speaker_data.get("text", "")
        evolution_msg = check_evolution(last_stage, {"stage": current_stage})
        
        # Handle XP for level up
        xp_gained = 0
        badges_earned = []
        if user_id and evolution_msg:
            progress = get_user_progress(user_id)
            progress["xp"] += XP_REWARDS["level_up"]
            if "level_up" not in progress["badges"]:
                progress["badges"].append("level_up")
                badges_earned.append(BADGES["level_up"])
            xp_gained = XP_REWARDS["level_up"]
            save_user_progress(user_id, progress)
        
        if evolution_msg:
            gamified = generate_gamified_prompt(current_stage, text, evolution=True)
            question = generate_reflective_question(text, reply_to)
            response_text = f"{evolution_msg}\n\n{question}\n\n{gamified['gamified_prompt']}"
        else:
            gamified = generate_gamified_prompt(last_stage if last_stage else current_stage, text)
            question = generate_reflective_question(text, reply_to)
            response_text = f"{question}\n\n{gamified['gamified_prompt']}"

        response_data = {
            "stage": current_stage,
            "question": question,
            "evolution": evolution_msg,
            "gamified": gamified
        }

        if user_id:
            response_data.update({
                "xp_gained": xp_gained,
                "badges_earned": badges_earned
            })

        return jsonify(response_data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# important
@app.route("/set_notification_time", methods=["POST"])
def set_notification_time():
    try:
        global NOTIFICATION_TIME
        data = request.get_json()
        new_time = data.get("time")
        
        # Validate time format
        try:
            hour, minute = map(int, new_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM"}), 400
        
        NOTIFICATION_TIME = new_time
        scheduler.remove_job("daily_task_notification")
        schedule_daily_notifications()
        
        return jsonify({"status": "success", "new_time": NOTIFICATION_TIME})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/send_welcome", methods=["POST"])
def send_welcome():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        fcm_token = data.get("fcm_token")

        if not user_id or not fcm_token:
            return jsonify({"error": "Missing user_id or fcm_token"}), 400

        # Send notification
        send_welcome_notification(fcm_token)

        # Log it in Firestore
        db.collection("users").document(user_id).collection("mergedMessages").add({
            "type": "welcome",
            "message": "What’s on your mind right now? Write or speak freely—no filters.",
            "timestamp": datetime.now(timezone.utc),
            "from": "system",
            "is_notification": True
        })

        return jsonify({"status": "success", "message": "Welcome notification sent"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    if FIREBASE_INITIALIZED:
        scheduler.start()
        schedule_daily_notifications()
    app.run(host="0.0.0.0", port=5000)

