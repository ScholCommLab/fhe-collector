"""
"""
import logging
from logging.handlers import RotatingFileHandler
import os
from psycopg2 import connect

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Create application and load settings."""
    app = Flask(__name__)

    print("* Flask Environment:", os.getenv("FLASK_ENV", default="NONE"))
    ENVIRONMENT = os.getenv("ENVIRONMENT", default="development")
    print("* User Environment:", ENVIRONMENT)
    if ENVIRONMENT == "development":
        print("* Loading Settings: User")
        app.config.from_pyfile(BASE_DIR + "/settings_user.py", silent=True)
        print("* Loading Settings: Development")
        app.config.from_pyfile(BASE_DIR + "/settings_development.py", silent=True)
        app.config.from_object("settings_default.Development")
        DebugToolbarExtension(app)
        print("* Database: " + app.config["SQLALCHEMY_DATABASE_URI"])
    elif ENVIRONMENT == "production":
        print("* Loading Settings: User")
        app.config.from_pyfile(BASE_DIR + "/settings_user.py", silent=True)
        print("* Loading Settings: Production")
        # order of settings loading: 1. settings file, 2. environment variable DATABASE_URL, 3. environment variable SQLALCHEMY_DATABASE_URI
        app.config.from_pyfile(BASE_DIR + "/settings_production.py", silent=True)
        app.config.from_object("settings_default.Production")
        print("* Database: " + app.config["SQLALCHEMY_DATABASE_URI"])
    elif ENVIRONMENT == "travis" or os.getenv("TRAVIS", default=False):
        print("* Loading Settings: Travis")
        app.config.from_object("settings_default.Travis")
    db.init_app(app)
    migrate.init_app(app, db)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    # scheduler = BackgroundScheduler()
    # rate_limit = app.config['FB_HOURLY_RATELIMIT']
    # rate_intervall = 3600 / rate_limit
    # scheduler.add_job(, trigger='interval', seconds=rate_intervall)
    # scheduler.start()

    if ENVIRONMENT == "production" or ENVIRONMENT == "development":

        # Logging (only production)
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/fhe.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Facebook Hidden Engagement")

    return app


from app import models
