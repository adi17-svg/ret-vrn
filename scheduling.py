
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from config import NOTIFICATION_TIME
# from notifications import send_all_daily_tasks  # Import function from notifications.py

# scheduler = BackgroundScheduler(daemon=True)
# JOB_ID = "daily_task_notification"

# def schedule_daily_notifications():
#     try:
#         # Remove previous job if it exists to avoid duplication
#         try:
#             scheduler.remove_job(JOB_ID)
#         except Exception:
#             pass  # No existing job to remove

#         hour, minute = map(int, NOTIFICATION_TIME.split(':'))
#         trigger = CronTrigger(hour=hour, minute=minute, timezone="UTC")

#         scheduler.add_job(
#             func=send_all_daily_tasks,
#             trigger=trigger,
#             id=JOB_ID,
#             replace_existing=True,
#             misfire_grace_time=60*60  # 1 hour grace period
#         )

#         if not scheduler.running:
#             scheduler.start()
#             print(f"⏰ Scheduled daily notifications at {NOTIFICATION_TIME} UTC")

#     except Exception as e:
#         print(f"⚠ Error scheduling notifications: {e}")

# #     return scheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from firebase_utils import db
# from notifications import send_morning_intention_notification

# scheduler = BackgroundScheduler(daemon=True)
# JOB_ID = "morning_intention_notification"


# def schedule_morning_intention():
#     """
#     Schedules ONLY the morning intention notification.
#     """

#     try:
#         # Remove old job if exists
#         try:
#             scheduler.remove_job(JOB_ID)
#         except Exception:
#             pass

#         # ⏰ Morning time (UTC)
#         trigger = CronTrigger(hour=7, minute=30, timezone="UTC")

#         def notify_all_users():
#             users_ref = db.collection("users").stream()

#             for user_doc in users_ref:
#                 user_data = user_doc.to_dict()
#                 fcm_token = user_data.get("fcm_token")

#                 if not fcm_token:
#                     continue

#                 send_morning_intention_notification(fcm_token)

#         scheduler.add_job(
#             func=notify_all_users,
#             trigger=trigger,
#             id=JOB_ID,
#             replace_existing=True,
#             misfire_grace_time=60 * 60
#         )

#         if not scheduler.running:
#             scheduler.start()

#         print("🌅 Morning intention scheduler started")

#     except Exception as e:
#         print(f"⚠ Error scheduling morning intention: {e}")

#     return scheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from firebase_utils import db
# from notifications import send_morning_intention_notification
# from config import MORNING_INTENTION_TIME

# scheduler = BackgroundScheduler(daemon=True)
# JOB_ID = "morning_intention_notification"


# def schedule_morning_intention():
#     """
#     Schedules ONLY the morning intention notification.
#     Time is controlled via Render ENV variable: MORNING_INTENTION_TIME (HH:MM in UTC)
#     """

#     try:
#         # 🔄 Remove old job if exists
#         try:
#             scheduler.remove_job(JOB_ID)
#         except Exception:
#             pass

#         # ⏰ Read time from ENV (default handled in config.py)
#         hour, minute = map(int, MORNING_INTENTION_TIME.split(":"))

#         trigger = CronTrigger(
#             hour=hour,
#             minute=minute,
#             timezone="UTC"
#         )

#         def notify_all_users():
#             users_ref = db.collection("users").stream()

#             for user_doc in users_ref:
#                 user_data = user_doc.to_dict()
#                 fcm_token = user_data.get("fcm_token")

#                 if not fcm_token:
#                     continue

#                 send_morning_intention_notification(fcm_token)

#         scheduler.add_job(
#             func=notify_all_users,
#             trigger=trigger,
#             id=JOB_ID,
#             replace_existing=True,
#             misfire_grace_time=60 * 60  # 1 hour grace
#         )

#         if not scheduler.running:
#             scheduler.start()

#         print(
#             f"🌅 Morning intention scheduler started at {MORNING_INTENTION_TIME} UTC"
#         )

#     except Exception as e:
#         print(f"⚠ Error scheduling morning intention: {e}")

# #     return scheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime, timezone
# from zoneinfo import ZoneInfo
# import os

# from firebase_utils import db
# from notifications import (
#     send_morning_intention_notification,
#     send_night_reflection_notification
# )

# # --------------------------------------------------
# # ENV CONFIG
# # --------------------------------------------------
# MORNING_TIME = os.getenv("MORNING_TIME", "09:00")  # HH:MM
# MORNING_GRACE_MINUTES = int(os.getenv("MORNING_GRACE_MINUTES", "10"))

# NIGHT_TIME = os.getenv("NIGHT_TIME", "21:30")  # HH:MM
# NIGHT_GRACE_MINUTES = int(os.getenv("NIGHT_GRACE_MINUTES", "15"))

# scheduler = BackgroundScheduler(daemon=True)


# # --------------------------------------------------
# # HELPERS
# # --------------------------------------------------
# def minutes_since_midnight(dt):
#     return dt.hour * 60 + dt.minute


# # --------------------------------------------------
# # MORNING SCHEDULER
# # --------------------------------------------------
# def schedule_morning_intention():
#     JOB_ID = "morning_intention_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)
#         today_utc = now_utc.date().isoformat()

#         users = db.collection("users").stream()

#         for user_doc in users:
#             user = user_doc.to_dict()
#             user_id = user_doc.id

#             fcm_token = user.get("fcm_token")
#             user_timezone = user.get("timezone")

#             if not fcm_token or not user_timezone:
#                 continue

#             if user.get("last_morning_notification_date") == today_utc:
#                 continue

#             try:
#                 user_now = now_utc.astimezone(ZoneInfo(user_timezone))
#             except Exception:
#                 continue

#             h, m = map(int, MORNING_TIME.split(":"))
#             now_minutes = minutes_since_midnight(user_now)
#             target_minutes = h * 60 + m

#             if target_minutes <= now_minutes <= target_minutes + MORNING_GRACE_MINUTES:
#                 send_morning_intention_notification(fcm_token)

#                 db.collection("users").document(user_id).set(
#                     {
#                         "last_morning_notification_date": today_utc,
#                         "last_morning_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # NIGHT SCHEDULER
# # --------------------------------------------------
# def schedule_night_reflection():
#     JOB_ID = "night_reflection_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)
#         today_utc = now_utc.date().isoformat()

#         users = db.collection("users").stream()

#         for user_doc in users:
#             user = user_doc.to_dict()
#             user_id = user_doc.id

#             fcm_token = user.get("fcm_token")
#             user_timezone = user.get("timezone")

#             if not fcm_token or not user_timezone:
#                 continue

#             if user.get("last_night_notification_date") == today_utc:
#                 continue

#             try:
#                 user_now = now_utc.astimezone(ZoneInfo(user_timezone))
#             except Exception:
#                 continue

#             h, m = map(int, NIGHT_TIME.split(":"))
#             now_minutes = minutes_since_midnight(user_now)
#             target_minutes = h * 60 + m

#             if target_minutes <= now_minutes <= target_minutes + NIGHT_GRACE_MINUTES:
#                 send_night_reflection_notification(fcm_token)

#                 db.collection("users").document(user_id).set(
#                     {
#                         "last_night_notification_date": today_utc,
#                         "last_night_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # START ALL SCHEDULERS
# # --------------------------------------------------
# def start_schedulers():
#     schedule_morning_intention()
#     schedule_night_reflection()

#     if not scheduler.running:
#         scheduler.start()

# #     print("🌅🌙 Morning & Night schedulers started")
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime, timezone, timedelta
# import os

# from firebase_utils import db
# from notifications import (
#     send_morning_intention_notification,
#     send_night_reflection_notification
# )

# # --------------------------------------------------
# # ENV CONFIG (USER LOCAL TIME)
# # --------------------------------------------------
# MORNING_TIME = os.getenv("MORNING_TIME", "09:00")  # HH:MM
# MORNING_GRACE_MINUTES = int(os.getenv("MORNING_GRACE_MINUTES", "10"))

# NIGHT_TIME = os.getenv("NIGHT_TIME", "21:30")  # HH:MM
# NIGHT_GRACE_MINUTES = int(os.getenv("NIGHT_GRACE_MINUTES", "15"))

# scheduler = BackgroundScheduler(daemon=True)

# # --------------------------------------------------
# # HELPERS
# # --------------------------------------------------
# def minutes_since_midnight(dt):
#     return dt.hour * 60 + dt.minute


# def get_user_now(now_utc, offset_minutes):
#     """
#     Convert UTC -> user local time using offset minutes.
#     """
#     return now_utc + timedelta(minutes=offset_minutes)


# # --------------------------------------------------
# # MORNING SCHEDULER
# # --------------------------------------------------
# def schedule_morning_intention():
#     JOB_ID = "morning_intention_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)
#         users = db.collection("users").stream()

#         for user_doc in users:
#             user = user_doc.to_dict()
#             user_id = user_doc.id

#             fcm_token = user.get("fcm_token")
#             offset = user.get("timezone_offset_minutes")

#             if not fcm_token or offset is None:
#                 continue

#             # --- user local time ---
#             user_now = get_user_now(now_utc, offset)
#             user_today = user_now.date().isoformat()

#             # --- already sent today (user-local) ---
#             if user.get("last_morning_notification_date") == user_today:
#                 continue

#             # --- target window ---
#             h, m = map(int, MORNING_TIME.split(":"))
#             now_minutes = minutes_since_midnight(user_now)
#             target_minutes = h * 60 + m

#             if target_minutes <= now_minutes <= target_minutes + MORNING_GRACE_MINUTES:
#                 send_morning_intention_notification(fcm_token)

#                 db.collection("users").document(user_id).set(
#                     {
#                         "last_morning_notification_date": user_today,
#                         "last_morning_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # NIGHT SCHEDULER
# # --------------------------------------------------
# def schedule_night_reflection():
#     JOB_ID = "night_reflection_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)
#         users = db.collection("users").stream()

#         for user_doc in users:
#             user = user_doc.to_dict()
#             user_id = user_doc.id

#             fcm_token = user.get("fcm_token")
#             offset = user.get("timezone_offset_minutes")

#             if not fcm_token or offset is None:
#                 continue

#             # --- user local time ---
#             user_now = get_user_now(now_utc, offset)
#             user_today = user_now.date().isoformat()

#             # --- already sent today (user-local) ---
#             if user.get("last_night_notification_date") == user_today:
#                 continue

#             # --- target window ---
#             h, m = map(int, NIGHT_TIME.split(":"))
#             now_minutes = minutes_since_midnight(user_now)
#             target_minutes = h * 60 + m

#             if target_minutes <= now_minutes <= target_minutes + NIGHT_GRACE_MINUTES:
#                 send_night_reflection_notification(fcm_token)

#                 db.collection("users").document(user_id).set(
#                     {
#                         "last_night_notification_date": user_today,
#                         "last_night_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # START ALL SCHEDULERS
# # --------------------------------------------------
# # def start_schedulers():
# #     schedule_morning_intention()
# #     schedule_night_reflection()

# #     if not scheduler.running:
# #         scheduler.start()

# #     print("🌅🌙 Morning & Night schedulers started")

# def start_schedulers():
#     global SCHEDULERS_STARTED

#     if SCHEDULERS_STARTED:
#         print("⛔ Schedulers already started, skipping")
#         return

#     schedule_morning_intention()
#     schedule_night_reflection()

#     if not scheduler.running:
#         scheduler.start()

#     SCHEDULERS_STARTED = True
# #     print("🌅🌙 Morning & Night schedulers started (single instance)")
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime, timezone, timedelta
# import os

# from firebase_utils import db
# from notifications import (
#     send_morning_intention_notification,
#     send_night_reflection_notification,
#     send_gratitude_notification,
#     send_cbt_reflection_notification,
#     send_awareness_checkin_notification,
# )

# # --------------------------------------------------
# # GLOBAL SAFETY FLAG
# # --------------------------------------------------
# SCHEDULERS_STARTED = False

# # --------------------------------------------------
# # ENV CONFIG (USER LOCAL TIME)
# # --------------------------------------------------
# MORNING_TIME = os.getenv("MORNING_TIME", "09:00")
# MORNING_GRACE_MINUTES = int(os.getenv("MORNING_GRACE_MINUTES", "10"))

# GRATITUDE_TIME = os.getenv("GRATITUDE_TIME", "13:00")
# CBT_TIME = os.getenv("CBT_TIME", "17:00")
# AWARENESS_TIME = os.getenv("AWARENESS_TIME", "20:00")

# NIGHT_TIME = os.getenv("NIGHT_TIME", "21:30")
# NIGHT_GRACE_MINUTES = int(os.getenv("NIGHT_GRACE_MINUTES", "15"))

# GENERIC_GRACE_MINUTES = 10

# scheduler = BackgroundScheduler(daemon=True)

# # --------------------------------------------------
# # HELPERS
# # --------------------------------------------------
# def minutes_since_midnight(dt):
#     return dt.hour * 60 + dt.minute


# def get_user_now(now_utc, offset_minutes):
#     return now_utc + timedelta(minutes=offset_minutes)


# # --------------------------------------------------
# # 🌅 MORNING INTENTION
# # --------------------------------------------------
# def schedule_morning_intention():
#     JOB_ID = "morning_intention_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)

#         for user_doc in db.collection("users").stream():
#             user = user_doc.to_dict()
#             uid = user_doc.id

#             token = user.get("fcm_token")
#             offset = user.get("timezone_offset_minutes")
#             if not token or offset is None:
#                 continue

#             user_now = get_user_now(now_utc, offset)
#             today = user_now.date().isoformat()

#             if user.get("last_morning_notification_date") == today:
#                 continue

#             h, m = map(int, MORNING_TIME.split(":"))
#             now_min = minutes_since_midnight(user_now)
#             target = h * 60 + m

#             if target <= now_min <= target + MORNING_GRACE_MINUTES:
#                 send_morning_intention_notification(token)
#                 db.collection("users").document(uid).set(
#                     {
#                         "last_morning_notification_date": today,
#                         "last_morning_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # 🌱 GRATITUDE JOURNAL
# # --------------------------------------------------
# def schedule_gratitude_journal():
#     JOB_ID = "gratitude_journal_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)

#         for user_doc in db.collection("users").stream():
#             user = user_doc.to_dict()
#             uid = user_doc.id

#             token = user.get("fcm_token")
#             offset = user.get("timezone_offset_minutes")
#             if not token or offset is None:
#                 continue

#             user_now = get_user_now(now_utc, offset)
#             today = user_now.date().isoformat()

#             if user.get("last_gratitude_notification_date") == today:
#                 continue

#             h, m = map(int, GRATITUDE_TIME.split(":"))
#             now_min = minutes_since_midnight(user_now)
#             target = h * 60 + m

#             if target <= now_min <= target + GENERIC_GRACE_MINUTES:
#                 send_gratitude_notification(token)
#                 db.collection("users").document(uid).set(
#                     {
#                         "last_gratitude_notification_date": today,
#                         "last_gratitude_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # 🧩 CBT REFLECTION
# # --------------------------------------------------
# def schedule_cbt_reflection():
#     JOB_ID = "cbt_reflection_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)

#         for user_doc in db.collection("users").stream():
#             user = user_doc.to_dict()
#             uid = user_doc.id

#             token = user.get("fcm_token")
#             offset = user.get("timezone_offset_minutes")
#             if not token or offset is None:
#                 continue

#             user_now = get_user_now(now_utc, offset)
#             today = user_now.date().isoformat()

#             if user.get("last_cbt_notification_date") == today:
#                 continue

#             h, m = map(int, CBT_TIME.split(":"))
#             now_min = minutes_since_midnight(user_now)
#             target = h * 60 + m

#             if target <= now_min <= target + GENERIC_GRACE_MINUTES:
#                 send_cbt_reflection_notification(token)
#                 db.collection("users").document(uid).set(
#                     {
#                         "last_cbt_notification_date": today,
#                         "last_cbt_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # 🌬️ AWARENESS CHECK-IN
# # --------------------------------------------------
# def schedule_awareness_checkin():
#     JOB_ID = "awareness_checkin_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)

#         for user_doc in db.collection("users").stream():
#             user = user_doc.to_dict()
#             uid = user_doc.id

#             token = user.get("fcm_token")
#             offset = user.get("timezone_offset_minutes")
#             if not token or offset is None:
#                 continue

#             user_now = get_user_now(now_utc, offset)
#             today = user_now.date().isoformat()

#             if user.get("last_awareness_notification_date") == today:
#                 continue

#             h, m = map(int, AWARENESS_TIME.split(":"))
#             now_min = minutes_since_midnight(user_now)
#             target = h * 60 + m

#             if target <= now_min <= target + GENERIC_GRACE_MINUTES:
#                 send_awareness_checkin_notification(token)
#                 db.collection("users").document(uid).set(
#                     {
#                         "last_awareness_notification_date": today,
#                         "last_awareness_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # 🌙 NIGHT REFLECTION
# # --------------------------------------------------
# def schedule_night_reflection():
#     JOB_ID = "night_reflection_windowed"

#     def notify_users():
#         now_utc = datetime.now(timezone.utc)

#         for user_doc in db.collection("users").stream():
#             user = user_doc.to_dict()
#             uid = user_doc.id

#             token = user.get("fcm_token")
#             offset = user.get("timezone_offset_minutes")
#             if not token or offset is None:
#                 continue

#             user_now = get_user_now(now_utc, offset)
#             today = user_now.date().isoformat()

#             if user.get("last_night_notification_date") == today:
#                 continue

#             h, m = map(int, NIGHT_TIME.split(":"))
#             now_min = minutes_since_midnight(user_now)
#             target = h * 60 + m

#             if target <= now_min <= target + NIGHT_GRACE_MINUTES:
#                 send_night_reflection_notification(token)
#                 db.collection("users").document(uid).set(
#                     {
#                         "last_night_notification_date": today,
#                         "last_night_notification_at": now_utc,
#                     },
#                     merge=True,
#                 )

#     scheduler.add_job(
#         notify_users,
#         CronTrigger(minute="*", timezone="UTC"),
#         id=JOB_ID,
#         replace_existing=True,
#     )


# # --------------------------------------------------
# # 🚀 START ALL SCHEDULERS (SAFE SINGLE INSTANCE)
# # --------------------------------------------------
# def start_schedulers():
#     global SCHEDULERS_STARTED

#     if SCHEDULERS_STARTED:
#         print("⛔ Schedulers already started, skipping")
#         return

#     schedule_morning_intention()
#     schedule_gratitude_journal()
#     schedule_cbt_reflection()
#     schedule_awareness_checkin()
#     schedule_night_reflection()

#     if not scheduler.running:
#         scheduler.start()

#     SCHEDULERS_STARTED = True
# # #     print("🌅🌱🧩🌬️🌙 All schedulers started (single instance)")
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime, timezone, timedelta
# import os

# from firebase_utils import db
# from notifications import (
#     send_morning_intention_notification,
#     send_night_reflection_notification,
#     send_gratitude_notification,
#     send_cbt_reflection_notification,
#     send_awareness_checkin_notification,
# )

# # ============================================================
# # 🔐 HARD SINGLE-SCHEDULER CONTROL
# # ============================================================
# IS_SCHEDULER_PROCESS = os.getenv("RUN_SCHEDULER", "false") == "true"
# SCHEDULERS_STARTED = False

# # ============================================================
# # ⏰ TIME CONFIG
# # ============================================================
# MORNING_TIME = os.getenv("MORNING_TIME", "09:00")
# MORNING_GRACE_MINUTES = int(os.getenv("MORNING_GRACE_MINUTES", "10"))

# GRATITUDE_TIME = os.getenv("GRATITUDE_TIME", "13:00")
# CBT_TIME = os.getenv("CBT_TIME", "17:00")
# AWARENESS_TIME = os.getenv("AWARENESS_TIME", "20:00")

# NIGHT_TIME = os.getenv("NIGHT_TIME", "21:30")
# NIGHT_GRACE_MINUTES = int(os.getenv("NIGHT_GRACE_MINUTES", "15"))

# GENERIC_GRACE_MINUTES = 10

# scheduler = BackgroundScheduler(daemon=True)

# # ============================================================
# # 🧠 HELPERS
# # ============================================================
# def minutes_since_midnight(dt):
#     return dt.hour * 60 + dt.minute


# def get_user_now(now_utc, offset_minutes):
#     return now_utc + timedelta(minutes=offset_minutes)


# def transactional_send(
#     user_ref,
#     user,
#     now_utc,
#     target_time,
#     grace,
#     last_key,
#     send_fn,
# ):
#     token = user.get("fcm_token")
#     offset = user.get("timezone_offset_minutes")

#     if not token or offset is None:
#         return

#     user_now = get_user_now(now_utc, offset)
#     today = user_now.date().isoformat()

#     if user.get(last_key) == today:
#         return

#     h, m = map(int, target_time.split(":"))
#     now_min = minutes_since_midnight(user_now)
#     target = h * 60 + m

#     if target <= now_min <= target + grace:
#         send_fn(token)
#         user_ref.update({
#             last_key: today,
#             f"{last_key}_at": now_utc,
#         })


# # ============================================================
# # 🌅 MORNING
# # ============================================================
# def schedule_morning_intention():
#     def job():
#         now_utc = datetime.now(timezone.utc)
#         for doc in db.collection("users").stream():
#             transactional_send(
#                 db.collection("users").document(doc.id),
#                 doc.to_dict() or {},
#                 now_utc,
#                 MORNING_TIME,
#                 MORNING_GRACE_MINUTES,
#                 "last_morning_notification_date",
#                 send_morning_intention_notification,
#             )

#     scheduler.add_job(job, CronTrigger(minute="*", timezone="UTC"), id="morning", replace_existing=True)


# # ============================================================
# # 🌱 GRATITUDE
# # ============================================================
# def schedule_gratitude():
#     def job():
#         now_utc = datetime.now(timezone.utc)
#         for doc in db.collection("users").stream():
#             transactional_send(
#                 db.collection("users").document(doc.id),
#                 doc.to_dict() or {},
#                 now_utc,
#                 GRATITUDE_TIME,
#                 GENERIC_GRACE_MINUTES,
#                 "last_gratitude_notification_date",
#                 send_gratitude_notification,
#             )

#     scheduler.add_job(job, CronTrigger(minute="*", timezone="UTC"), id="gratitude", replace_existing=True)


# # ============================================================
# # 🧩 CBT
# # ============================================================
# def schedule_cbt():
#     def job():
#         now_utc = datetime.now(timezone.utc)
#         for doc in db.collection("users").stream():
#             transactional_send(
#                 db.collection("users").document(doc.id),
#                 doc.to_dict() or {},
#                 now_utc,
#                 CBT_TIME,
#                 GENERIC_GRACE_MINUTES,
#                 "last_cbt_notification_date",
#                 send_cbt_reflection_notification,
#             )

#     scheduler.add_job(job, CronTrigger(minute="*", timezone="UTC"), id="cbt", replace_existing=True)


# # ============================================================
# # 🌬️ AWARENESS
# # ============================================================
# def schedule_awareness():
#     def job():
#         now_utc = datetime.now(timezone.utc)
#         for doc in db.collection("users").stream():
#             transactional_send(
#                 db.collection("users").document(doc.id),
#                 doc.to_dict() or {},
#                 now_utc,
#                 AWARENESS_TIME,
#                 GENERIC_GRACE_MINUTES,
#                 "last_awareness_notification_date",
#                 send_awareness_checkin_notification,
#             )

#     scheduler.add_job(job, CronTrigger(minute="*", timezone="UTC"), id="awareness", replace_existing=True)


# # ============================================================
# # 🌙 NIGHT
# # ============================================================
# def schedule_night():
#     def job():
#         now_utc = datetime.now(timezone.utc)
#         for doc in db.collection("users").stream():
#             transactional_send(
#                 db.collection("users").document(doc.id),
#                 doc.to_dict() or {},
#                 now_utc,
#                 NIGHT_TIME,
#                 NIGHT_GRACE_MINUTES,
#                 "last_night_notification_date",
#                 send_night_reflection_notification,
#             )

#     scheduler.add_job(job, CronTrigger(minute="*", timezone="UTC"), id="night", replace_existing=True)


# # ============================================================
# # 🚀 START
# # ============================================================
# def start_schedulers():
#     global SCHEDULERS_STARTED

#     if not IS_SCHEDULER_PROCESS:
#         print("⛔ Scheduler disabled on this worker")
#         return

#     if SCHEDULERS_STARTED:
#         return

#     schedule_morning_intention()
#     schedule_gratitude()
#     schedule_cbt()
#     schedule_awareness()
#     schedule_night()

#     scheduler.start()
#     SCHEDULERS_STARTED = True
#     print("✅ Scheduler started (SINGLE INSTANCE)")
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
import os

from firebase_utils import db
from notifications import (
    send_morning_intention_notification,
    send_night_reflection_notification,
    send_gratitude_notification,
    send_cbt_reflection_notification,
    send_awareness_checkin_notification,
)

# ============================================================
# 🔐 SINGLE SCHEDULER CONTROL
# ============================================================

IS_SCHEDULER_PROCESS = os.getenv("RUN_SCHEDULER", "false") == "true"
SCHEDULERS_STARTED = False

# ============================================================
# ⏰ TIME CONFIG (24h format)
# ============================================================

MORNING_TIME = os.getenv("MORNING_TIME", "09:00")
GRATITUDE_TIME = os.getenv("GRATITUDE_TIME", "13:00")
CBT_TIME = os.getenv("CBT_TIME", "17:00")
AWARENESS_TIME = os.getenv("AWARENESS_TIME", "20:00")
NIGHT_TIME = os.getenv("NIGHT_TIME", "21:30")

scheduler = BackgroundScheduler(daemon=True)

# ============================================================
# 🧠 HELPERS
# ============================================================

def get_user_now(now_utc, offset_minutes):
    return now_utc + timedelta(minutes=offset_minutes)


def transactional_send(
    user_ref,
    user,
    now_utc,
    target_time,
    last_key,
    send_fn,
):
    try:
        token = user.get("fcm_token")
        offset = user.get("timezone_offset_minutes")

        print("--------------------------------------------------")
        print("👤 Checking user:", user_ref.id)
        print("🕒 UTC NOW:", now_utc)

        if not token:
            print("❌ No FCM token")
            return

        if offset is None:
            print("❌ No timezone offset")
            return

        user_now = get_user_now(now_utc, offset)
        today = user_now.date().isoformat()

        print("🕒 User local time:", user_now)
        print("📅 Today (user):", today)
        print("🎯 Target time:", target_time)

        # Already sent today?
        if user.get(last_key) == today:
            print("⛔ Already sent today")
            return

        h, m = map(int, target_time.split(":"))

        print("🧮 Comparing →",
              "User hour:", user_now.hour,
              "User minute:", user_now.minute)

        # EXACT MATCH (no grace)
        if user_now.hour == h and user_now.minute == m:
            print("🚀 TIME MATCH — Sending notification")

            result = send_fn(token)
            print("📨 Firebase response:", result)

            user_ref.update({
                last_key: today,
                f"{last_key}_at": now_utc,
            })

            print("✅ Firestore updated")

        else:
            print("⌛ Not matching minute")

    except Exception as e:
        print("🔥 ERROR in transactional_send:", e)


# ============================================================
# 🌅 MORNING
# ============================================================

def schedule_morning_intention():
    def job():
        now_utc = datetime.now(timezone.utc)
        for doc in db.collection("users").stream():
            transactional_send(
                db.collection("users").document(doc.id),
                doc.to_dict() or {},
                now_utc,
                MORNING_TIME,
                "last_morning_notification_date",
                send_morning_intention_notification,
            )

    scheduler.add_job(
        job,
        CronTrigger(minute="*", timezone="UTC"),
        id="morning",
        replace_existing=True,
    )


# ============================================================
# 🌱 GRATITUDE
# ============================================================

def schedule_gratitude():
    def job():
        now_utc = datetime.now(timezone.utc)
        for doc in db.collection("users").stream():
            transactional_send(
                db.collection("users").document(doc.id),
                doc.to_dict() or {},
                now_utc,
                GRATITUDE_TIME,
                "last_gratitude_notification_date",
                send_gratitude_notification,
            )

    scheduler.add_job(
        job,
        CronTrigger(minute="*", timezone="UTC"),
        id="gratitude",
        replace_existing=True,
    )


# ============================================================
# 🧩 CBT
# ============================================================

def schedule_cbt():
    def job():
        now_utc = datetime.now(timezone.utc)
        for doc in db.collection("users").stream():
            transactional_send(
                db.collection("users").document(doc.id),
                doc.to_dict() or {},
                now_utc,
                CBT_TIME,
                "last_cbt_notification_date",
                send_cbt_reflection_notification,
            )

    scheduler.add_job(
        job,
        CronTrigger(minute="*", timezone="UTC"),
        id="cbt",
        replace_existing=True,
    )


# ============================================================
# 🌬️ AWARENESS
# ============================================================

def schedule_awareness():
    def job():
        now_utc = datetime.now(timezone.utc)
        for doc in db.collection("users").stream():
            transactional_send(
                db.collection("users").document(doc.id),
                doc.to_dict() or {},
                now_utc,
                AWARENESS_TIME,
                "last_awareness_notification_date",
                send_awareness_checkin_notification,
            )

    scheduler.add_job(
        job,
        CronTrigger(minute="*", timezone="UTC"),
        id="awareness",
        replace_existing=True,
    )


# ============================================================
# 🌙 NIGHT
# ============================================================

def schedule_night():
    def job():
        now_utc = datetime.now(timezone.utc)
        for doc in db.collection("users").stream():
            transactional_send(
                db.collection("users").document(doc.id),
                doc.to_dict() or {},
                now_utc,
                NIGHT_TIME,
                "last_night_notification_date",
                send_night_reflection_notification,
            )

    scheduler.add_job(
        job,
        CronTrigger(minute="*", timezone="UTC"),
        id="night",
        replace_existing=True,
    )


# ============================================================
# 🚀 START
# ============================================================

def start_schedulers():
    global SCHEDULERS_STARTED

    if not IS_SCHEDULER_PROCESS:
        print("⛔ Scheduler disabled on this worker")
        return

    if SCHEDULERS_STARTED:
        return

    print("🚀 Starting schedulers...")

    schedule_morning_intention()
    schedule_gratitude()
    schedule_cbt()
    schedule_awareness()
    schedule_night()

    scheduler.start()
    SCHEDULERS_STARTED = True

    print("✅ Scheduler started (SINGLE INSTANCE)")
