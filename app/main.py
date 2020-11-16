# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/ScholCommLab/fhe-collector.

Copyright 2018 Stefan Kasberger

Licensed under the MIT License.
"""
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
import os

from app.bp.api import blueprint as api_blueprint
from app.bp.api.v1 import blueprint as api_v1_blueprint
from app.bp.main import blueprint as main_blueprint
from app.config import get_config, get_config_name
from app.db import get_db, close_db, init_app, init_db
from app.models import Base, db

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


migrate = Migrate()


def create_app(test_config: str = None) -> Flask:
    """Create application and load settings."""
    print("* Start FHE Collector...")

    if test_config is None:
        load_dotenv()
        config_name = get_config_name()
    else:
        config_name = test_config

    config = get_config(config_name)

    app = Flask("fhe_collector", root_path=ROOT_DIR)
    app.config.from_object(config)
    config.init_app(app)

    init_app(app)
    db.init_app(app)

    migrate.init_app(app, db)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(api_v1_blueprint, url_prefix="/api/v1")

    print(' * Settings "{0}" loaded'.format(config_name))
    print(" * Database: " + app.config["SQLALCHEMY_DATABASE_URI"])
    print(" * Environment: " + app.config["FLASK_ENV"])

    return app
