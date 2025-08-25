# import os
# import json
# from datetime import datetime
# import random

# SPIRAL_TASKS = [
#     # Add your spiral task strings here, for example:
#     "Recall a moment when you felt truly grateful.",
#     "Describe your current mindset in one word.",
#     "What motivates you to get out of bed each day?",
#     # ... add all other question prompts as needed
# ]

# DAILY_TASKS_FILE = "daily_tasks.json"
# COMPLETED_TASKS_FILE = "completed_tasks.json"
# USER_PROGRESS_FILE = "user_progress.json"

# def init_task_files():
#     """Initialize required JSON files if they do not already exist."""
#     for file_path in [COMPLETED_TASKS_FILE, DAILY_TASKS_FILE, USER_PROGRESS_FILE]:
#         if not os.path.exists(file_path):
#             with open(file_path, "w") as f:
#                 if file_path == USER_PROGRESS_FILE:
#                     json.dump({}, f)
#                 else:
#                     json.dump([], f)

# def generate_daily_task():
#     """Generate or retrieve today's shared daily task."""
#     today = datetime.utcnow().date().isoformat()
#     try:
#         with open(DAILY_TASKS_FILE, "r") as f:
#             tasks = json.load(f)
#     except Exception:
#         tasks = []

#     # Check if a task already exists for today
#     existing_task = next((t for t in tasks if t.get("date") == today), None)
#     if existing_task:
#         return existing_task

#     # If none exists, choose a random new task and save it
#     task_content = random.choice(SPIRAL_TASKS)
#     task_data = {
#         "user_id": "all",  # Indicates this is the shared daily task
#         "task": task_content,
#         "date": today,
#         "completed": False,
#         "timestamp": datetime.utcnow().isoformat()
#     }
#     tasks.append(task_data)
#     try:
#         with open(DAILY_TASKS_FILE, "w") as f:
#             json.dump(tasks, f, indent=2)
#     except Exception as e:
#         print("Error saving daily task:", e)
#     return task_data

# def save_completed_task(user_id, task_data):
#     """
#     Save the completion status of a daily task for a given user.
#     """
#     try:
#         with open(COMPLETED_TASKS_FILE, "r") as f:
#             tasks = json.load(f)
#     except Exception:
#         tasks = []

#     completed_entry = {
#         "user_id": user_id,
#         "task": task_data.get("task"),
#         "stage": task_data.get("stage"),
#         "date": datetime.utcnow().date().isoformat(),
#         "completed": True,
#         "timestamp": datetime.utcnow().isoformat(),
#         "completion_timestamp": datetime.utcnow().isoformat()
#     }
#     tasks.append(completed_entry)

#     try:
#         with open(COMPLETED_TASKS_FILE, "w") as f:
#             json.dump(tasks, f, indent=2)
#     except Exception as e:
#         print("Error saving completed task:", e)
import os
import json
from datetime import datetime, timedelta
import random

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

DAILY_TASKS_FILE = "daily_tasks.json"
COMPLETED_TASKS_FILE = "completed_tasks.json"
USER_PROGRESS_FILE = "user_progress.json"

def init_task_files():
    """Initialize required JSON files if they do not already exist."""
    for file_path in [COMPLETED_TASKS_FILE, DAILY_TASKS_FILE, USER_PROGRESS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                if file_path == USER_PROGRESS_FILE:
                    json.dump({}, f)
                else:
                    json.dump([], f)

def generate_daily_task():
    """Generate or retrieve today's shared daily task."""
    today = datetime.utcnow().date().isoformat()
    try:
        with open(DAILY_TASKS_FILE, "r") as f:
            tasks = json.load(f)
    except Exception:
        tasks = []

    # Check if a task already exists for today
    existing_task = next((t for t in tasks if t.get("date") == today), None)
    if existing_task:
        return existing_task

    # If none exists, choose a random new task and save it
    task_content = random.choice(SPIRAL_TASKS)
    task_data = {
        "user_id": "all",  # Indicates this is the shared daily task
        "task": task_content,
        "date": today,
        "completed": False,
        "timestamp": datetime.utcnow().isoformat()
    }
    tasks.append(task_data)
    try:
        with open(DAILY_TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print("Error saving daily task:", e)
    return task_data

def save_completed_task(user_id, task_data):
    """
    Save the completion status of a daily task for a given user.
    """
    try:
        with open(COMPLETED_TASKS_FILE, "r") as f:
            tasks = json.load(f)
    except Exception:
        tasks = []

    completed_entry = {
        "user_id": user_id,
        "task": task_data.get("task"),
        "stage": task_data.get("stage"),
        "date": datetime.utcnow().date().isoformat(),
        "completed": True,
        "timestamp": datetime.utcnow().isoformat(),
        "completion_timestamp": datetime.utcnow().isoformat()
    }
    tasks.append(completed_entry)

    try:
        with open(COMPLETED_TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print("Error saving completed task:", e)

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