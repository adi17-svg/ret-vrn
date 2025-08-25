# from flask import Flask
# from flask_cors import CORS
# from routes import bp  # Import your routes blueprint from routes.py

# def create_app():
#     """
#     Application factory function to create and configure the Flask app.
#     """
#     app = Flask(__name__)

#     # Enable CORS for cross-origin requests
#     CORS(app)

#     # Register blueprints (routes)
#     app.register_blueprint(bp)

#     # Start any schedulers or background jobs (e.g., daily notifications)
#     from scheduling import schedule_daily_notifications
#     schedule_daily_notifications()

#     return app
from flask import Flask
from flask_cors import CORS
from routes import bp  # Import the routes blueprint from routes.py

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)  # Use __name__, not _name_
    app.config.from_object("config")  # Load config from config.py

    # Enable CORS to allow cross-origin requests
    CORS(app)

    # Register the routes blueprint
    app.register_blueprint(bp)

    # Start scheduling any background tasks like daily notifications
    from scheduling import schedule_daily_notifications
    schedule_daily_notifications()

    return app