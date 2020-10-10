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

    FLASK_ENV = os.getenv("FLASK_ENV", default="NONE")
    print("* Environment:", FLASK_ENV)
    app.config.from_json(os.getenv("YOURAPPLICATION_SETTINGS"))
    print("* Settings User: Loaded")
    is_travis = os.getenv("TRAVIS", default=False)

    if FLASK_ENV == "development" and not is_travis:
        app.config.from_object("settings_default.Development")
        print("* Settings Development: Loaded")
        DebugToolbarExtension(app)
    elif FLASK_ENV == "production" and not is_travis:
        app.config.from_object("settings_default.Production")
        print("* Settings Production: Loaded")
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

    elif is_travis:
        app.config.from_object("settings_default.Travis")
        print("* Settings Travis: Loaded")
    print("* Database: " + app.config["SQLALCHEMY_DATABASE_URI"])
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

    return app


from app import models
