# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/ScholCommLab/fhe-collector.

Copyright 2018 Stefan Kasberger

Licensed under the MIT License.
"""
import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import g


__author__ = "Stefan Kasberger"
__email__ = "mail@stefankasberger.at"
__copyright__ = "Copyright (c) 2018 Stefan Kasberger"
__license__ = "MIT License"
__version__ = "0.1.0"
__url__ = "https://github.com/ScholCommLab/fhe-collector"


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
db = SQLAlchemy()
migrate = Migrate()


def create_instance_dir(instance_dir):
    try:
        os.makedirs(instance_dir)
    except OSError:
        pass


def create_app(test_config=None):
    """Create application and load settings."""
    app = Flask(__name__, instance_relative_config=True)

    if "APP_SETTINGS" in os.environ:
        app.config["APP_SETTINGS"] = os.getenv("APP_SETTINGS", default=None)

    if "TESTING" in os.environ:
        app.config["TESTING"] = os.getenv("TESTING")

    # Load test_config dict()
    if test_config is not None:
        app.config.update(test_config)
        print("* Settings create_app() #1: Loaded")

    # Load instance specific default settings and setup instance
    if app.config["TESTING"]:
        if os.getenv("TRAVIS", default=False):
            app.config.from_object("fhe_collector.settings_default.Travis")
        else:
            create_instance_dir(app.instance_path)
            app.config.from_object("fhe_collector.settings_default.Testing")
    else:
        if app.config["FLASK_ENV"] == "development":
            from flask_debugtoolbar import DebugToolbarExtension

            DebugToolbarExtension(app)
            app.config.from_object("fhe_collector.settings_default.Development")
        elif app.config["FLASK_ENV"] == "production":
            # Logging (only production)
            import logging
            from logging.handlers import RotatingFileHandler

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

            app.config.from_object("fhe_collector.settings_default.Production")

    # Load app settings
    if "APP_SETTINGS" in os.environ or "APP_SETTINGS" in app.config:
        app.config.from_json(app.config["APP_SETTINGS"])
    if "API_TOKEN" in os.environ:
        app.config["API_TOKEN"] = os.getenv("API_TOKEN", default=None)
    if "CSV_FILENAME" in os.environ:
        app.config["CSV_FILENAME"] = os.getenv("CSV_FILENAME", default=None)
    if "ADMIN_EMAIL" in os.environ:
        app.config["ADMIN_EMAIL"] = os.getenv("ADMIN_EMAIL", default=None)
    if "APP_EMAIL" in os.environ:
        app.config["APP_EMAIL"] = os.getenv("APP_EMAIL", default=None)
    if "SECRET_KEY" in os.environ:
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", default=None)
    if "NCBI_TOOL" in os.environ:
        app.config["NCBI_TOOL"] = os.getenv("NCBI_TOOL", default=None)
    if "FB_APP_ID" in os.environ:
        app.config["FB_APP_ID"] = os.getenv("FB_APP_ID", default=None)
    if "FB_APP_SECRET" in os.environ:
        app.config["FB_APP_SECRET"] = os.getenv("FB_APP_SECRET", default=None)
    if "FB_HOURLY_RATELIMIT" in os.environ:
        app.config["FB_HOURLY_RATELIMIT"] = os.getenv(
            "FB_HOURLY_RATELIMIT", default=None
        )
    if "FB_BATCH_SIZE" in os.environ:
        app.config["FB_BATCH_SIZE"] = os.getenv("FB_BATCH_SIZE", default=None)
    if "URL_BATCH_SIZE" in os.environ:
        app.config["URL_BATCH_SIZE"] = os.getenv("URL_BATCH_SIZE", default=None)
    print("* Settings App: Loaded")

    if test_config is not None:
        app.config.update(test_config)
        print("* Settings create_app() #2: Loaded")

    print("* Settings Loading: FINISHED")
    print("* Database: " + app.config["SQLALCHEMY_DATABASE_URI"])

    from fhe_collector.database import init_app as db_init_app

    db_init_app(app)
    db.init_app(app)

    migrate.init_app(app, db)

    from fhe_collector.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from fhe_collector.main import bp as main_bp

    app.register_blueprint(main_bp)

    from fhe_collector.api import bp as api_bp

    app.register_blueprint(api_bp)

    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "Doi": Doi, "Url": Url}

    # scheduler = BackgroundScheduler()
    # rate_limit = app.config['FB_HOURLY_RATELIMIT']
    # rate_intervall = 3600 / rate_limit
    # scheduler.add_job(, trigger='interval', seconds=rate_intervall)
    # scheduler.start()

    return app
