# # from flask import Flask
# # from flask_cors import CORS
# # from routes import bp  # Import your routes blueprint from routes.py

# # def create_app():
# #     """
# #     Application factory function to create and configure the Flask app.
# #     """
# #     app = Flask(__name__)

# #     # Enable CORS for cross-origin requests
# #     CORS(app)

# #     # Register blueprints (routes)
# #     app.register_blueprint(bp)

# #     # Start any schedulers or background jobs (e.g., daily notifications)
# #     from scheduling import schedule_daily_notifications
# #     schedule_daily_notifications()

# # #     return app
# from flask import Flask
# from flask_cors import CORS
# from routes import bp  # Import the routes blueprint from routes.py

# def create_app():
#     """
#     Application factory function to create and configure the Flask app.
#     """
#     app = Flask(__name__)  # Use __name__, not _name_
#     app.config.from_object("config")  # Load config from config.py

#     # Enable CORS to allow cross-origin requests
#     CORS(app)

#     # Register the routes blueprint
#     app.register_blueprint(bp)

#     # Start scheduling any background tasks like daily notifications
#     from scheduling import schedule_daily_notifications
#     schedule_daily_notifications()

# #     return app
# from flask import Flask
# from flask_cors import CORS
# from routes import bp
# from notifications import bp as notifications_bp


# def create_app():
#     """
#     Application factory function to create and configure the Flask app.
#     """
#     app = Flask(__name__)
#     app.config.from_object("config")

#     # Enable CORS
#     CORS(app)

#     # Register blueprints
#     app.register_blueprint(bp)
#     app.register_blueprint(notifications_bp)

#     # 🔥 START ONLY MORNING INTENTION SCHEDULER
#     from scheduling import schedule_morning_intention
#     schedule_morning_intention()

#     return app
from flask import Flask
from flask_cors import CORS

# Main API routes
from routes import bp

# Notification routes (optional APIs like /set_intention)
from notifications import bp as notifications_bp


def create_app():
    """
    Application factory function
    """
    app = Flask(__name__)
    app.config.from_object("config")

    # --------------------------------------------------
    # CORS
    # --------------------------------------------------
    CORS(app)

    # --------------------------------------------------
    # REGISTER BLUEPRINTS
    # --------------------------------------------------
    app.register_blueprint(bp)
    app.register_blueprint(notifications_bp)

    # --------------------------------------------------
    # 🔔 START SCHEDULERS (MORNING + NIGHT)
    # --------------------------------------------------
    from scheduling import start_schedulers
    start_schedulers()

    return app
