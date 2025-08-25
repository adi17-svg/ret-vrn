import json
from datetime import datetime, timedelta
from tasks import USER_PROGRESS_FILE

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
    except Exception:
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
        # Already updated today; return current streak
        return progress["streak"]
    
    if last_active and (datetime.fromisoformat(last_active).date() + timedelta(days=1)) == datetime.utcnow().date():
        # Continue the streak
        progress["streak"] += 1
    else:
        # Reset streak
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