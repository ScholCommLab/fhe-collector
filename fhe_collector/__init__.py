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
from config import config


__author__ = "Stefan Kasberger"
__email__ = "mail@stefankasberger.at"
__copyright__ = "Copyright (c) 2018 Stefan Kasberger"
__license__ = "MIT License"
__version__ = "0.1.0"
__url__ = "https://github.com/ScholCommLab/fhe-collector"


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name="default"):
    """Create application and load settings."""
    print("* Start FHE Collector...")

    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    print(' * Settings "{0}": Loaded'.format(config_name))
    print(" * Settings Loading: FINISHED")
    print("   - Database: " + app.config["SQLALCHEMY_DATABASE_URI"])
    print("   - Environment: " + app.config["FLASK_ENV"])

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

    print("* End")
    return app
