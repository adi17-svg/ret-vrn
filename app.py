
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os
# import openai
# import traceback
# import requests
# import json
# from datetime import datetime, timedelta
# from collections import defaultdict

# # Load environment variables
# load_dotenv()
# a4f_api_key = os.getenv("A4F_API_KEY")
# assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")

# if not a4f_api_key or not assemblyai_api_key:
#     raise ValueError("❌ Missing A4F or AssemblyAI API key in .env")

# # Setup A4F GPT-compatible client using legacy OpenAI SDK
# openai.api_key = a4f_api_key
# openai.api_base = "https://api.a4f.co/v1"

# app = Flask(__name__)
# CORS(app)

# STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

# COMPLETED_TASKS_FILE = "completed_tasks.json"
# DAILY_TASKS_FILE = "daily_tasks.json"

# def init_task_files():
#     for file_path in [COMPLETED_TASKS_FILE, DAILY_TASKS_FILE]:
#         if not os.path.exists(file_path):
#             with open(file_path, "w") as f:
#                 json.dump([], f)

# init_task_files()

# def save_completed_task(user_id, task_data):
#     try:
#         with open(COMPLETED_TASKS_FILE, "r") as f:
#             tasks = json.load(f)

#         tasks.append({
#             "user_id": user_id,
#             "task": task_data.get("task"),
#             "stage": task_data.get("stage"),
#             "date": datetime.utcnow().date().isoformat(),
#             "completed": True,
#             "timestamp": datetime.utcnow().isoformat(),
#             "completion_timestamp": datetime.utcnow().isoformat()
#         })

#         with open(COMPLETED_TASKS_FILE, "w") as f:
#             json.dump(tasks, f, indent=2)
#     except Exception as e:
#         print("Error saving completed task:", e)

# def get_user_tasks(user_id, file_path):
#     try:
#         with open(file_path, "r") as f:
#             tasks = json.load(f)
#         return [t for t in tasks if t.get("user_id") == user_id]
#     except Exception as e:
#         print(f"Error reading {file_path}:", e)
#         return []

# def save_daily_task(task_data):
#     try:
#         with open(DAILY_TASKS_FILE, "r") as f:
#             tasks = json.load(f)

#         tasks = [t for t in tasks if not (
#             t.get("user_id") == task_data.get("user_id") and 
#             t.get("date") == task_data.get("date")
#         )]

#         tasks.append(task_data)

#         with open(DAILY_TASKS_FILE, "w") as f:
#             json.dump(tasks, f, indent=2)
#     except Exception as e:
#         print("Error saving daily task:", e)

# def generate_daily_task_content():
#     prompt = (
#         "Generate one brief self-reflection task for personal growth. "
#         "It should be simple enough to complete in 1-2 minutes. "
#         "Examples: 'Notice when you feel resistance today', 'Identify one value you honored today', "
#         "'Recall a moment you felt truly alive today'. "
#         "Respond with just the task, no explanations."
#     )
#     response = openai.ChatCompletion.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.7,
#     )
#     return response.choices[0].message["content"].strip()

# def generate_daily_task(user_id):
#     today = datetime.utcnow().date().isoformat()
#     task_content = generate_daily_task_content()
    
#     task_data = {
#         "user_id": user_id,
#         "task": task_content,
#         "date": today,
#         "completed": False,
#         "timestamp": datetime.utcnow().isoformat()
#     }
    
#     save_daily_task(task_data)
#     return task_data

# @app.route("/daily_task", methods=["GET"])
# def get_daily_task():
#     try:
#         user_id = request.args.get("user_id")
#         if not user_id:
#             return jsonify({"error": "Missing user_id"}), 400
            
#         today = datetime.utcnow().date().isoformat()
        
#         user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
#         today_task = next((t for t in user_tasks if t.get("date") == today), None)
        
#         if today_task:
#             return jsonify(today_task)
        
#         new_task = generate_daily_task(user_id)
#         return jsonify(new_task)
        
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/complete_task", methods=["POST"])
# def complete_task():
#     try:
#         data = request.get_json()
#         user_id = data.get("user_id")
#         task_id = data.get("task_id")

#         if not user_id or not task_id:
#             return jsonify({"error": "Missing user_id or task_id"}), 400

#         with open(DAILY_TASKS_FILE, "r") as f:
#             daily_tasks = json.load(f)
            
#         task_to_complete = None
#         for task in daily_tasks:
#             if str(task.get("timestamp")) == task_id and task.get("user_id") == user_id:
#                 task["completed"] = True
#                 task["completion_timestamp"] = datetime.utcnow().isoformat()
#                 task_to_complete = task
#                 break
                
#         if not task_to_complete:
#             return jsonify({"error": "Task not found"}), 404
            
#         with open(DAILY_TASKS_FILE, "w") as f:
#             json.dump(daily_tasks, f, indent=2)
        
#         save_completed_task(user_id, task_to_complete)
            
#         return jsonify({"message": "Task marked as completed"})
        
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/task_history", methods=["GET"])
# def get_task_history():
#     try:
#         user_id = request.args.get("user_id")
#         if not user_id:
#             return jsonify({"error": "Missing user_id"}), 400
            
#         completed_tasks = get_user_tasks(user_id, COMPLETED_TASKS_FILE)
#         return jsonify(completed_tasks)
        
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# def detect_intent(entry):
#     prompt = (
#         "You are a Spiral Dynamics gatekeeper.\n"
#         "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
#         "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
#         "Reply with one word only: 'spiral' or 'chat'.\n\n"
#         f"Entry: \"{entry}\""
#     )
#     response = openai.ChatCompletion.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0,
#     )
#     return "spiral" if "spiral" in response.choices[0].message["content"].lower() else "chat"

# def classify_stage(entry):
#     prompt = (
#         f"Analyze the user's entry and return only the Spiral Dynamics stage (one of: {', '.join(STAGES)}). "
#         f"Respond only with the stage name.\n\n"
#         f"Entry: \"{entry}\""
#     )
#     response = openai.ChatCompletion.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.6,
#     )
#     return response.choices[0].message["content"].strip()

# def generate_reflective_question(entry, reply_to=None):
#     context = f"\nReplying to: \"{reply_to}\"" if reply_to else ""
#     prompt = (
#         f"You are a Spiral Dynamics mentor. Based on the user's thoughts{context}, "
#         f"ask one deep, emotionally resonant question. "
#         f"Don't mention Spiral Dynamics. Don't explain anything. Just ask the question.\n\n"
#         f"User message: \"{entry}\""
#     )
#     response = openai.ChatCompletion.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.85,
#     )
#     return response.choices[0].message["content"].strip()

# def generate_growth_prompt(entry, stage):
#     prompt = (
#         f"User is currently reflecting at Spiral Dynamics stage: {stage}. "
#         f"Based on this short journal entry, give one brief nudge or thought that could help them evolve. "
#         f"Don't say it's a growth tip. Don't label it. Just give a sentence that feels natural and empowering.\n\n"
#         f"Entry: \"{entry}\""
#     )
#     response = openai.ChatCompletion.create(
#         model="provider-3/gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.8,
#     )
#     return response.choices[0].message["content"].strip()

# def check_evolution(last_stage, current_stage):
#     try:
#         if last_stage and current_stage and STAGES.index(current_stage) > STAGES.index(last_stage):
#             return f"🌱 Beautiful shift! You've evolved to {current_stage} — keep growing 🌟"
#     except:
#         pass
#     return None

# @app.route("/merged", methods=["POST"])
# def merged_reflection():
#     try:
#         data = request.get_json()
#         entry = data.get("text", "").strip()
#         last_stage = data.get("last_stage", "").strip()
#         reply_to = data.get("reply_to", "").strip()

#         if not entry:
#             return jsonify({"error": "Missing journaling input."}), 400

#         intent = detect_intent(entry)

#         if intent == "chat":
#             message = f"User: {reply_to}\n\nUser response: {entry}" if reply_to else entry
#             reply = openai.ChatCompletion.create(
#                 model="provider-3/gpt-4",
#                 messages=[{"role": "user", "content": f"You are a kind friend. Respond casually to: {message}"}],
#                 temperature=0.7,
#             )
#             return jsonify({
#                 "mode": "chat",
#                 "response": reply.choices[0].message["content"].strip()
#             })

#         stage = classify_stage(entry)
#         question = generate_reflective_question(entry, reply_to)
#         evolution_msg = check_evolution(last_stage, stage)
#         growth = generate_growth_prompt(entry, stage)

#         return jsonify({
#             "mode": "spiral",
#             "stage": stage,
#             "question": question,
#             "evolution": evolution_msg,
#             "growth": growth
#         })

#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/reflect_transcription", methods=["POST"])
# def reflect_from_audio():
#     try:
#         if "file" not in request.files:
#             return jsonify({"error": "Missing audio file"}), 400

#         reply_to = request.form.get("reply_to", "").strip()
#         last_stage = request.form.get("last_stage", "").strip()
#         audio_file = request.files["file"]

#         upload_response = requests.post(
#             "https://api.assemblyai.com/v2/upload",
#             headers={
#                 "authorization": assemblyai_api_key,
#                 "content-type": "application/octet-stream"
#             },
#             data=audio_file.read()
#         )
#         upload_response.raise_for_status()
#         audio_url = upload_response.json()["upload_url"]

#         transcript_response = requests.post(
#             "https://api.assemblyai.com/v2/transcript",
#             headers={
#                 "authorization": assemblyai_api_key,
#                 "content-type": "application/json"
#             },
#             json={
#                 "audio_url": audio_url,
#                 "speaker_labels": True,
#                 "punctuate": True,
#                 "format_text": True,
#                 "language_code": "en_us"
#             }
#         )
#         transcript_response.raise_for_status()
#         transcript_id = transcript_response.json()["id"]

#         while True:
#             poll = requests.get(
#                 f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
#                 headers={"authorization": assemblyai_api_key}
#             )
#             result = poll.json()
#             if result["status"] in ("completed", "error"):
#                 break

#         if result["status"] == "error":
#             return jsonify({"error": f"Transcription failed: {result.get('error')}"}), 500

#         utterances = result.get("utterances", [])
#         if not utterances:
#             return jsonify({"error": "No utterances found."}), 400

#         combined_text = " ".join([u["text"] for u in utterances]).strip()
#         transcript = "\n".join([f"Speaker {u['speaker']}: {u['text']}" for u in utterances])

#         intent = detect_intent(combined_text)
        
#         if intent == "spiral":
#             stage = classify_stage(combined_text)
#             question = generate_reflective_question(combined_text, reply_to)
#             evolution_msg = check_evolution(last_stage, stage)
#             growth = generate_growth_prompt(combined_text, stage)

#             return jsonify({
#                 "mode": "spiral",
#                 "stage": stage,
#                 "question": question,
#                 "evolution": evolution_msg,
#                 "growth": growth,
#                 "transcription": transcript
#             })
#         else:
#             message = f"User: {reply_to}\n\nUser response: {combined_text}" if reply_to else combined_text
#             reply = openai.ChatCompletion.create(
#                 model="provider-3/gpt-4",
#                 messages=[{"role": "user", "content": f"You are a kind friend. Respond casually to: {message}"}],
#                 temperature=0.7,
#             )
#             return jsonify({
#                 "mode": "chat",
#                 "response": reply.choices[0].message["content"].strip(),
#                 "transcription": transcript
#             })

#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/completed_tasks", methods=["GET"])
# def get_completed_tasks():
#     try:
#         if not os.path.exists(COMPLETED_TASKS_FILE):
#             return jsonify([])
#         with open(COMPLETED_TASKS_FILE, "r") as f:
#             tasks = json.load(f)
#         return jsonify(tasks)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/complete_task_old", methods=["POST"])
# def complete_task_old():
#     try:
#         data = request.get_json()
#         user_id = data.get("user_id")
#         task = data.get("task")

#         if not user_id or not task:
#             return jsonify({"error": "Missing user_id or task"}), 400

#         save_completed_task(user_id, {"task": task})
#         return jsonify({"message": "Task saved."})
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)

# new task daily
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os
# import openai
# import traceback
# import json
# from datetime import datetime, timedelta
# import random

# # Load environment variables
# load_dotenv()
# a4f_api_key = os.getenv("A4F_API_KEY")
# assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")

# if not a4f_api_key or not assemblyai_api_key:
#     raise ValueError("❌ Missing A4F or AssemblyAI API key in .env")

# openai.api_key = a4f_api_key
# openai.api_base = "https://api.a4f.co/v1"

# app = Flask(__name__)
# CORS(app)

# STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]
# COMPLETED_TASKS_FILE = "completed_tasks.json"
# DAILY_TASKS_FILE = "daily_tasks.json"

# SPIRAL_TASKS = [
#     "Recall a time when your only focus was to make it through the day. What mattered most in that moment?",
#     "When your basic needs aren't met, how does your mindset change?",
#     "Think of a moment when safety or food felt uncertain. How did you respond?",
#     "Are there superstitions or rituals you follow without fully knowing why? What do they mean to you?",
#     "Describe a tradition your family follows that makes you feel rooted. Why is it important?",
#     "How do you stay connected to your ancestry, roots, or community?",
#     "Have you ever acted on impulse just because it felt right in the moment? What happened?",
#     "Describe a time when you took control of a situation without waiting for permission. Why did you do it?",
#     "When do you feel most powerful or in control?",
#     "How do you deal with people who challenge your authority or choices?",
#     "What moral code or set of values do you try to live by? How did you come to believe in it?",
#     "Think of a time you followed a rule that you didn’t fully agree with. Why did you do it?",
#     "What does loyalty mean to you, and who deserves it?",
#     "When someone breaks a rule or law, what’s your first reaction — curiosity, anger, or something else?",
#     "What does success mean to you beyond financial gain? How do you measure your progress?",
#     "Have you ever pushed yourself too hard to prove something to others? Why did it matter so much?",
#     "How do you react when someone limits your freedom or questions your ability?",
#     "What’s a personal goal that you're proud of achieving? What drove you to it?",
#     "Is competition a healthy part of life for you? Why or why not?",
#     "When was the last time you deeply empathized with someone you disagreed with? What did you learn?",
#     "How do you decide when to speak up for others versus stay quiet for harmony?",
#     "Think of a group or cause you care about. Why does it matter to you?",
#     "Do you believe in absolute truths, or is everything relative to context?",
#     "How do you handle tension when people don’t feel heard?",
#     "Do you ever hide your opinions to keep peace? How does that affect you?",
#     "Have you ever realized both sides of an argument were valid? How did you respond?",
#     "Do you ever switch perspectives just to understand something more deeply?",
#     "Describe a moment when you helped two opposing views find common ground.",
#     "What’s more important to you — being right, or being helpful in a larger system?",
#     "How do you handle paradoxes or contradictions in life?",
#     "Have you ever felt part of something much larger than yourself? What was that experience like?",
#     "How do you define harmony — is it internal, collective, spiritual?",
#     "When do you feel most connected to all forms of life or nature?",
#     "Describe a time you made a decision that honored both logic and intuition.",
#     "What does planetary well-being mean to you?",
#     "Have your values changed over the years? What sparked the shift?",
#     "When do you feel most authentic — when leading, listening, creating, or something else?",
#     "What role does tradition play in your life today?",
#     "When you disagree with someone close to you, do you debate, reflect, or avoid?",
#     "What part of your identity do you feel is constantly evolving?",
#     "Do you feel you have a personal truth? How did you discover it?",
#     "How do you know when it’s time to move on from a belief?",
#     "If someone asked why you do what you do, how would you explain your purpose?",
#     "When you’re uncertain, what guides your choices — logic, values, instinct, or something else?",
#     "What does freedom mean to you right now?",
#     "Have you ever tried to influence others' beliefs? Why or why not?",
#     "Do you often seek answers, or feel okay with not knowing?",
#     "Do you adapt your behavior depending on the environment or people around you?",
#     "When was the last time you questioned your worldview?",
#     "If everyone followed your philosophy of life, what kind of world would we have?",
#     "Do you trust people easily? Why or why not?",
#     "What do you feel you’ve outgrown, mentally or emotionally?",
#     "Do you often feel pulled in different directions — between structure, freedom, purpose, and peace?",
#     "Do you value clarity or complexity more when making sense of life?",
#     "What type of change feels threatening to you, and why?",
#     "What type of change feels exciting to you, and why?",
#     "How do you decide what’s worth standing up for?",
#     "What kind of legacy feels meaningful to leave behind?",
#     "What does growth mean to you?",
#     "If you could fully express your truth without fear, what would you say?"
# ]

# def init_task_files():
#     for file_path in [COMPLETED_TASKS_FILE, DAILY_TASKS_FILE]:
#         if not os.path.exists(file_path):
#             with open(file_path, "w") as f:
#                 json.dump([], f)

# init_task_files()

# def get_user_tasks(user_id, file_path):
#     try:
#         with open(file_path, "r") as f:
#             tasks = json.load(f)
#         return [t for t in tasks if t.get("user_id") == user_id]
#     except:
#         return []

# def get_recent_tasks(user_id, n_days=30):
#     user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
#     cutoff = datetime.utcnow().date() - timedelta(days=n_days)
#     return [t['task'] for t in user_tasks if datetime.fromisoformat(t['date']).date() >= cutoff]

# def save_daily_task(task_data):
#     with open(DAILY_TASKS_FILE, "r") as f:
#         tasks = json.load(f)
#     tasks = [t for t in tasks if not (t.get("user_id") == task_data["user_id"] and t.get("date") == task_data["date"])]
#     tasks.append(task_data)
#     with open(DAILY_TASKS_FILE, "w") as f:
#         json.dump(tasks, f, indent=2)

# def generate_daily_task_content(user_id, recent_tasks):
#     available = [task for task in SPIRAL_TASKS if task not in recent_tasks]
#     if not available:
#         available = SPIRAL_TASKS[:]
#     return random.choice(available)

# def generate_daily_task(user_id):
#     today = datetime.utcnow().date().isoformat()
#     recent_tasks = get_recent_tasks(user_id, n_days=30)

#     user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
#     existing_today_task = next((t for t in user_tasks if t.get("date") == today), None)

#     # Only replace if today's task is a duplicate from last 30 days
#     if existing_today_task:
#         if existing_today_task['task'] not in recent_tasks[:-1]:
#             return existing_today_task  # Accept today's if not in recent duplicates

#     task_content = generate_daily_task_content(user_id, recent_tasks)
#     task_data = {
#         "user_id": user_id,
#         "task": task_content,
#         "date": today,
#         "completed": False,
#         "timestamp": datetime.utcnow().isoformat()
#     }

#     save_daily_task(task_data)
#     return task_data

# @app.route("/daily_task", methods=["GET"])
# def get_daily_task():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400
#     return jsonify(generate_daily_task(user_id))

# @app.route("/complete_task", methods=["POST"])
# def complete_task():
#     data = request.get_json()
#     user_id = data.get("user_id")
#     task_id = data.get("task_id")
#     if not user_id or not task_id:
#         return jsonify({"error": "Missing user_id or task_id"}), 400
#     with open(DAILY_TASKS_FILE, "r") as f:
#         daily_tasks = json.load(f)
#     for task in daily_tasks:
#         if task["user_id"] == user_id and task["timestamp"] == task_id:
#             task["completed"] = True
#             task["completion_timestamp"] = datetime.utcnow().isoformat()
#             save_completed_task(user_id, task)
#             with open(DAILY_TASKS_FILE, "w") as f:
#                 json.dump(daily_tasks, f, indent=2)
#             return jsonify({"message": "Task marked as completed"})
#     return jsonify({"error": "Task not found"}), 404

# def save_completed_task(user_id, task_data):
#     with open(COMPLETED_TASKS_FILE, "r") as f:
#         tasks = json.load(f)
#     tasks.append({
#         "user_id": user_id,
#         "task": task_data.get("task"),
#         "stage": task_data.get("stage"),
#         "date": datetime.utcnow().date().isoformat(),
#         "completed": True,
#         "timestamp": datetime.utcnow().isoformat(),
#         "completion_timestamp": datetime.utcnow().isoformat()
#     })
#     with open(COMPLETED_TASKS_FILE, "w") as f:
#         json.dump(tasks, f, indent=2)

# @app.route("/task_history", methods=["GET"])
# def get_task_history():
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400
#     return jsonify(get_user_tasks(user_id, COMPLETED_TASKS_FILE))

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os
# import openai
# import traceback
# import requests
# import json
# from datetime import datetime, timedelta
# from collections import defaultdict
# import random

# # Load environment variables
# load_dotenv()
# a4f_api_key = os.getenv("A4F_API_KEY")
# assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")

# if not a4f_api_key or not assemblyai_api_key:
#     raise ValueError("❌ Missing A4F or AssemblyAI API key in .env")

# # Setup A4F GPT-compatible client using legacy OpenAI SDK
# openai.api_key = a4f_api_key
# openai.api_base = "https://api.a4f.co/v1"

# app = Flask(__name__)
# CORS(app)

# STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

# COMPLETED_TASKS_FILE = "completed_tasks.json"
# DAILY_TASKS_FILE = "daily_tasks.json"

# SPIRAL_TASKS = [
#     "Recall a time when your only focus was to make it through the day. What mattered most in that moment?",
#     "When your basic needs aren't met, how does your mindset change?",
#     "Think of a moment when safety or food felt uncertain. How did you respond?",
#     "Are there superstitions or rituals you follow without fully knowing why? What do they mean to you?",
#     "Describe a tradition your family follows that makes you feel rooted. Why is it important?",
#     "How do you stay connected to your ancestry, roots, or community?",
#     "Have you ever acted on impulse just because it felt right in the moment? What happened?",
#     "Describe a time when you took control of a situation without waiting for permission. Why did you do it?",
#     "When do you feel most powerful or in control?",
#     "How do you deal with people who challenge your authority or choices?",
#     "What moral code or set of values do you try to live by? How did you come to believe in it?",
#     "Think of a time you followed a rule that you didn't fully agree with. Why did you do it?",
#     "What does loyalty mean to you, and who deserves it?",
#     "When someone breaks a rule or law, what's your first reaction — curiosity, anger, or something else?",
#     "What does success mean to you beyond financial gain? How do you measure your progress?",
#     "Have you ever pushed yourself too hard to prove something to others? Why did it matter so much?",
#     "How do you react when someone limits your freedom or questions your ability?",
#     "What's a personal goal that you're proud of achieving? What drove you to it?",
#     "Is competition a healthy part of life for you? Why or why not?",
#     "When was the last time you deeply empathized with someone you disagreed with? What did you learn?",
#     "How do you decide when to speak up for others versus stay quiet for harmony?",
#     "Think of a group or cause you care about. Why does it matter to you?",
#     "Do you believe in absolute truths, or is everything relative to context?",
#     "How do you handle tension when people don't feel heard?",
#     "Do you ever hide your opinions to keep peace? How does that affect you?",
#     "Have you ever realized both sides of an argument were valid? How did you respond?",
#     "Do you ever switch perspectives just to understand something more deeply?",
#     "Describe a moment when you helped two opposing views find common ground.",
#     "What's more important to you — being right, or being helpful in a larger system?",
#     "How do you handle paradoxes or contradictions in life?",
#     "Have you ever felt part of something much larger than yourself? What was that experience like?",
#     "How do you define harmony — is it internal, collective, spiritual?",
#     "When do you feel most connected to all forms of life or nature?",
#     "Describe a time you made a decision that honored both logic and intuition.",
#     "What does planetary well-being mean to you?",
#     "Have your values changed over the years? What sparked the shift?",
#     "When do you feel most authentic — when leading, listening, creating, or something else?",
#     "What role does tradition play in your life today?",
#     "When you disagree with someone close to you, do you debate, reflect, or avoid?",
#     "What part of your identity do you feel is constantly evolving?",
#     "Do you feel you have a personal truth? How did you discover it?",
#     "How do you know when it's time to move on from a belief?",
#     "If someone asked why you do what you do, how would you explain your purpose?",
#     "When you're uncertain, what guides your choices — logic, values, instinct, or something else?",
#     "What does freedom mean to you right now?",
#     "Have you ever tried to influence others' beliefs? Why or why not?",
#     "Do you often seek answers, or feel okay with not knowing?",
#     "Do you adapt your behavior depending on the environment or people around you?",
#     "When was the last time you questioned your worldview?",
#     "If everyone followed your philosophy of life, what kind of world would we have?",
#     "Do you trust people easily? Why or why not?",
#     "What do you feel you've outgrown, mentally or emotionally?",
#     "Do you often feel pulled in different directions — between structure, freedom, purpose, and peace?",
#     "Do you value clarity or complexity more when making sense of life?",
#     "What type of change feels threatening to you, and why?",
#     "What type of change feels exciting to you, and why?",
#     "How do you decide what's worth standing up for?",
#     "What kind of legacy feels meaningful to leave behind?",
#     "What does growth mean to you?",
#     "If you could fully express your truth without fear, what would you say?"
# ]

# def init_task_files():
#     for file_path in [COMPLETED_TASKS_FILE, DAILY_TASKS_FILE]:
#         if not os.path.exists(file_path):
#             with open(file_path, "w") as f:
#                 json.dump([], f)

# init_task_files()

# def save_completed_task(user_id, task_data):
#     try:
#         with open(COMPLETED_TASKS_FILE, "r") as f:
#             tasks = json.load(f)

#         tasks.append({
#             "user_id": user_id,
#             "task": task_data.get("task"),
#             "stage": task_data.get("stage"),
#             "date": datetime.utcnow().date().isoformat(),
#             "completed": True,
#             "timestamp": datetime.utcnow().isoformat(),
#             "completion_timestamp": datetime.utcnow().isoformat()
#         })

#         with open(COMPLETED_TASKS_FILE, "w") as f:
#             json.dump(tasks, f, indent=2)
#     except Exception as e:
#         print("Error saving completed task:", e)

# def get_user_tasks(user_id, file_path):
#     try:
#         with open(file_path, "r") as f:
#             tasks = json.load(f)
#         return [t for t in tasks if t.get("user_id") == user_id]
#     except Exception as e:
#         print(f"Error reading {file_path}:", e)
#         return []

# def get_recent_tasks(user_id, n_days=30):
#     user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
#     cutoff = datetime.utcnow().date() - timedelta(days=n_days)
#     return [t['task'] for t in user_tasks if datetime.fromisoformat(t['date']).date() >= cutoff]

# def save_daily_task(task_data):
#     try:
#         with open(DAILY_TASKS_FILE, "r") as f:
#             tasks = json.load(f)

#         tasks = [t for t in tasks if not (
#             t.get("user_id") == task_data.get("user_id") and 
#             t.get("date") == task_data.get("date")
#         )]

#         tasks.append(task_data)

#         with open(DAILY_TASKS_FILE, "w") as f:
#             json.dump(tasks, f, indent=2)
#     except Exception as e:
#         print("Error saving daily task:", e)

# def generate_daily_task_content(user_id, recent_tasks):
#     available = [task for task in SPIRAL_TASKS if task not in recent_tasks]
#     if not available:
#         available = SPIRAL_TASKS[:]
#     return random.choice(available)

# def generate_daily_task(user_id):
#     today = datetime.utcnow().date().isoformat()
#     recent_tasks = get_recent_tasks(user_id, n_days=30)

#     user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
#     existing_today_task = next((t for t in user_tasks if t.get("date") == today), None)

#     # Only replace if today's task is a duplicate from last 30 days
#     if existing_today_task:
#         if existing_today_task['task'] not in recent_tasks[:-1]:
#             return existing_today_task  # Accept today's if not in recent duplicates

#     task_content = generate_daily_task_content(user_id, recent_tasks)
#     task_data = {
#         "user_id": user_id,
#         "task": task_content,
#         "date": today,
#         "completed": False,
#         "timestamp": datetime.utcnow().isoformat()
#     }
    
#     save_daily_task(task_data)
#     return task_data

# @app.route("/daily_task", methods=["GET"])
# def get_daily_task():
#     try:
#         user_id = request.args.get("user_id")
#         if not user_id:
#             return jsonify({"error": "Missing user_id"}), 400
            
#         return jsonify(generate_daily_task(user_id))
        
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/complete_task", methods=["POST"])
# def complete_task():
#     try:
#         data = request.get_json()
#         user_id = data.get("user_id")
#         task_id = data.get("task_id")

#         if not user_id or not task_id:
#             return jsonify({"error": "Missing user_id or task_id"}), 400

#         with open(DAILY_TASKS_FILE, "r") as f:
#             daily_tasks = json.load(f)
            
#         task_to_complete = None
#         for task in daily_tasks:
#             if str(task.get("timestamp")) == task_id and task.get("user_id") == user_id:
#                 task["completed"] = True
#                 task["completion_timestamp"] = datetime.utcnow().isoformat()
#                 task_to_complete = task
#                 break
                
#         if not task_to_complete:
#             return jsonify({"error": "Task not found"}), 404
            
#         with open(DAILY_TASKS_FILE, "w") as f:
#             json.dump(daily_tasks, f, indent=2)
        
#         save_completed_task(user_id, task_to_complete)
            
#         return jsonify({"message": "Task marked as completed"})
        
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/task_history", methods=["GET"])
# def get_task_history():
#     try:
#         user_id = request.args.get("user_id")
#         if not user_id:
#             return jsonify({"error": "Missing user_id"}), 400
            
#         completed_tasks = get_user_tasks(user_id, COMPLETED_TASKS_FILE)
#         return jsonify(completed_tasks)
        
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai
import traceback
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import random

# Load environment variables
load_dotenv()
a4f_api_key = os.getenv("A4F_API_KEY")
assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")

if not a4f_api_key or not assemblyai_api_key:
    raise ValueError("❌ Missing A4F or AssemblyAI API key in .env")

# Setup A4F GPT-compatible client using legacy OpenAI SDK
openai.api_key = a4f_api_key
openai.api_base = "https://api.a4f.co/v1"

app = Flask(__name__)
CORS(app)

STAGES = ["Beige", "Purple", "Red", "Blue", "Orange", "Green", "Yellow", "Turquoise"]

COMPLETED_TASKS_FILE = "completed_tasks.json"
DAILY_TASKS_FILE = "daily_tasks.json"

SPIRAL_TASKS = [
    # (same task list as before – unchanged)
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

def init_task_files():
    for file_path in [COMPLETED_TASKS_FILE, DAILY_TASKS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump([], f)

init_task_files()

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

def get_user_tasks(user_id, file_path):
    try:
        with open(file_path, "r") as f:
            tasks = json.load(f)
        return [t for t in tasks if t.get("user_id") == user_id]
    except Exception as e:
        print(f"Error reading {file_path}:", e)
        return []

def get_recent_tasks(user_id, n_days=30):
    user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
    cutoff = datetime.utcnow().date() - timedelta(days=n_days)
    return [t['task'] for t in user_tasks if datetime.fromisoformat(t['date']).date() >= cutoff]

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

def generate_daily_task_content(user_id, recent_tasks):
    available = [task for task in SPIRAL_TASKS if task not in recent_tasks]
    if not available:
        available = SPIRAL_TASKS[:]
    return random.choice(available)

def generate_daily_task(user_id):
    today = datetime.utcnow().date().isoformat()

    user_tasks = get_user_tasks(user_id, DAILY_TASKS_FILE)
    existing_today_task = next((t for t in user_tasks if t.get("date") == today), None)
    if existing_today_task:
        return existing_today_task

    recent_tasks = get_recent_tasks(user_id, n_days=30)
    task_content = generate_daily_task_content(user_id, recent_tasks)
    task_data = {
        "user_id": user_id,
        "task": task_content,
        "date": today,
        "completed": False,
        "timestamp": datetime.utcnow().isoformat()
    }

    save_daily_task(task_data)
    return task_data

@app.route("/daily_task", methods=["GET"])
def get_daily_task():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
            
        return jsonify(generate_daily_task(user_id))
        
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

# 👇 The rest of your journaling & audio endpoints remain UNTOUCHED below
# (/merged, /reflect_transcription, etc.)

# (Keep your current implementations from previous working version — unchanged)

def detect_intent(entry):
    prompt = (
        "You are a Spiral Dynamics gatekeeper.\n"
        "Determine if this journal entry reflects emotional expression, life struggle, desire for change, personal values, reflection, or self-awareness.\n"
        "If yes, return 'spiral'. If it's only surface-level chat, jokes, or small talk, return 'chat'.\n"
        "Reply with one word only: 'spiral' or 'chat'.\n\n"
        f"Entry: \"{entry}\""
    )
    response = openai.ChatCompletion.create(
        model="provider-3/gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return "spiral" if "spiral" in response.choices[0].message["content"].lower() else "chat"

def classify_stage(entry):
    prompt = (
        f"Analyze the user's entry and return only the Spiral Dynamics stage (one of: {', '.join(STAGES)}). "
        f"Respond only with the stage name.\n\n"
        f"Entry: \"{entry}\""
    )
    response = openai.ChatCompletion.create(
        model="provider-3/gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    return response.choices[0].message["content"].strip()

def generate_reflective_question(entry, reply_to=None):
    context = f"\nReplying to: \"{reply_to}\"" if reply_to else ""
    prompt = (
        f"You are a Spiral Dynamics mentor. Based on the user's thoughts{context}, "
        f"ask one deep, emotionally resonant question. "
        f"Don't mention Spiral Dynamics. Don't explain anything. Just ask the question.\n\n"
        f"User message: \"{entry}\""
    )
    response = openai.ChatCompletion.create(
        model="provider-3/gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
    )
    return response.choices[0].message["content"].strip()

def generate_growth_prompt(entry, stage):
    prompt = (
        f"User is currently reflecting at Spiral Dynamics stage: {stage}. "
        f"Based on this short journal entry, give one brief nudge or thought that could help them evolve. "
        f"Don't say it's a growth tip. Don't label it. Just give a sentence that feels natural and empowering.\n\n"
        f"Entry: \"{entry}\""
    )
    response = openai.ChatCompletion.create(
        model="provider-3/gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.choices[0].message["content"].strip()

def check_evolution(last_stage, current_stage):
    try:
        if last_stage and current_stage and STAGES.index(current_stage) > STAGES.index(last_stage):
            return f"🌱 Beautiful shift! You've evolved to {current_stage} — keep growing 🌟"
    except:
        pass
    return None

@app.route("/merged", methods=["POST"])
def merged_reflection():
    try:
        data = request.get_json()
        entry = data.get("text", "").strip()
        last_stage = data.get("last_stage", "").strip()
        reply_to = data.get("reply_to", "").strip()

        if not entry:
            return jsonify({"error": "Missing journaling input."}), 400

        intent = detect_intent(entry)

        if intent == "chat":
            message = f"User: {reply_to}\n\nUser response: {entry}" if reply_to else entry
            reply = openai.ChatCompletion.create(
                model="provider-3/gpt-4",
                messages=[{"role": "user", "content": f"You are a kind friend. Respond casually to: {message}"}],
                temperature=0.7,
            )
            return jsonify({
                "mode": "chat",
                "response": reply.choices[0].message["content"].strip()
            })

        stage = classify_stage(entry)
        question = generate_reflective_question(entry, reply_to)
        evolution_msg = check_evolution(last_stage, stage)
        growth = generate_growth_prompt(entry, stage)

        return jsonify({
            "mode": "spiral",
            "stage": stage,
            "question": question,
            "evolution": evolution_msg,
            "growth": growth
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/reflect_transcription", methods=["POST"])
def reflect_from_audio():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Missing audio file"}), 400

        reply_to = request.form.get("reply_to", "").strip()
        last_stage = request.form.get("last_stage", "").strip()
        audio_file = request.files["file"]

        upload_response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers={
                "authorization": assemblyai_api_key,
                "content-type": "application/octet-stream"
            },
            data=audio_file.read()
        )
        upload_response.raise_for_status()
        audio_url = upload_response.json()["upload_url"]

        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={
                "authorization": assemblyai_api_key,
                "content-type": "application/json"
            },
            json={
                "audio_url": audio_url,
                "speaker_labels": True,
                "punctuate": True,
                "format_text": True,
                "language_code": "en_us"
            }
        )
        transcript_response.raise_for_status()
        transcript_id = transcript_response.json()["id"]

        while True:
            poll = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers={"authorization": assemblyai_api_key}
            )
            result = poll.json()
            if result["status"] in ("completed", "error"):
                break

        if result["status"] == "error":
            return jsonify({"error": f"Transcription failed: {result.get('error')}"}), 500

        utterances = result.get("utterances", [])
        if not utterances:
            return jsonify({"error": "No utterances found."}), 400

        combined_text = " ".join([u["text"] for u in utterances]).strip()
        transcript = "\n".join([f"Speaker {u['speaker']}: {u['text']}" for u in utterances])

        intent = detect_intent(combined_text)
        
        if intent == "spiral":
            stage = classify_stage(combined_text)
            question = generate_reflective_question(combined_text, reply_to)
            evolution_msg = check_evolution(last_stage, stage)
            growth = generate_growth_prompt(combined_text, stage)

            return jsonify({
                "mode": "spiral",
                "stage": stage,
                "question": question,
                "evolution": evolution_msg,
                "growth": growth,
                "transcription": transcript
            })
        else:
            message = f"User: {reply_to}\n\nUser response: {combined_text}" if reply_to else combined_text
            reply = openai.ChatCompletion.create(
                model="provider-3/gpt-4",
                messages=[{"role": "user", "content": f"You are a kind friend. Respond casually to: {message}"}],
                temperature=0.7,
            )
            return jsonify({
                "mode": "chat",
                "response": reply.choices[0].message["content"].strip(),
                "transcription": transcript
            })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/completed_tasks", methods=["GET"])
def get_completed_tasks():
    try:
        if not os.path.exists(COMPLETED_TASKS_FILE):
            return jsonify([])
        with open(COMPLETED_TASKS_FILE, "r") as f:
            tasks = json.load(f)
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/complete_task_old", methods=["POST"])
def complete_task_old():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        task = data.get("task")

        if not user_id or not task:
            return jsonify({"error": "Missing user_id or task"}), 400

        save_completed_task(user_id, {"task": task})
        return jsonify({"message": "Task saved."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)