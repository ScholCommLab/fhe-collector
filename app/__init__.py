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


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name="default"):
    """Create application and load settings."""
    print("* Start FHE Collector...")

    app = Flask("fhe_collector", root_path=ROOT_DIR)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    print(' * Settings "{0}": Loaded'.format(config_name))
    print(" * Database: " + app.config["SQLALCHEMY_DATABASE_URI"])
    print(" * Environment: " + app.config["FLASK_ENV"])

    from app.database import init_app as db_init_app

    db_init_app(app)
    db.init_app(app)

    migrate.init_app(app, db)

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    print("* End")
    return app
