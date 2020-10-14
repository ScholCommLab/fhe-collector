# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test factory."""
import os
from fhe_collector import create_app
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


def test_config_development():
    app = create_app(
        {
            "FLASK_ENV": "development",
            "APP_SETTINGS": "settings_development.json",
            "SQLALCHEMY_DATABASE_URI": "postgresql://localhost/fhe_collector",
        }
    )
    assert False == app.testing
    assert True == app.config["DEBUG"]
    assert False == app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert app.config["SQLALCHEMY_DATABASE_URI"]
    assert app.config["API_TOKEN"]
    assert app.config["CSV_FILENAME"]
    assert app.config["ADMIN_EMAIL"]
    assert app.config["APP_EMAIL"]
    assert app.config["SECRET_KEY"]
    assert app.config["NCBI_TOOL"]
    assert app.config["FB_APP_ID"]
    assert app.config["FB_APP_SECRET"]
    assert app.config["FB_HOURLY_RATELIMIT"]
    assert app.config["FB_BATCH_SIZE"]
    assert app.config["URL_BATCH_SIZE"]


def test_config_testing(app):
    assert True == app.testing
    assert True == app.config["DEBUG"]
    assert False == app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert (
        "postgresql://localhost/fhe_collector_test"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert app.config["API_TOKEN"]
    assert app.config["CSV_FILENAME"]
    assert app.config["ADMIN_EMAIL"]
    assert app.config["APP_EMAIL"]
    assert app.config["SECRET_KEY"]
    assert app.config["NCBI_TOOL"]
    assert app.config["FB_APP_ID"]
    assert app.config["FB_APP_SECRET"]
    assert app.config["FB_HOURLY_RATELIMIT"]
    assert app.config["FB_BATCH_SIZE"]
    assert app.config["URL_BATCH_SIZE"]


def test_config_testing_travis():
    app = create_app(
        {
            "TESTING": True,
            "TRAVIS": True,
            "APP_SETTINGS": "settings_testing_localhost.json",
            "SQLALCHEMY_DATABASE_URI": "postgresql://localhost/fhe_collector_test",
        }
    )
    assert True == app.config["TRAVIS"]
    assert True == app.testing
    assert True == app.config["DEBUG"]
    assert False == app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert app.config["SQLALCHEMY_DATABASE_URI"]
    assert app.config["API_TOKEN"]
    assert app.config["CSV_FILENAME"]
    assert app.config["ADMIN_EMAIL"]
    assert app.config["APP_EMAIL"]
    assert app.config["SECRET_KEY"]
    assert app.config["NCBI_TOOL"]
    assert app.config["FB_APP_ID"]
    assert app.config["FB_APP_SECRET"]
    assert app.config["FB_HOURLY_RATELIMIT"]
    assert app.config["FB_BATCH_SIZE"]
    assert app.config["URL_BATCH_SIZE"]


def test_config_production():
    app = create_app(
        {
            "FLASK_ENV": "production",
            "APP_SETTINGS": "settings_production.json",
            "SQLALCHEMY_DATABASE_URI": "postgresql://localhost/fhe_collector",
        }
    )
    assert False == app.testing
    assert False == app.config["DEBUG"]
    assert False == app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert (
        "postgresql://localhost/fhe_collector" == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert app.config["API_TOKEN"]
    assert app.config["CSV_FILENAME"]
    assert app.config["ADMIN_EMAIL"]
    assert app.config["APP_EMAIL"]
    assert app.config["SECRET_KEY"]
    assert app.config["NCBI_TOOL"]
    assert app.config["FB_APP_ID"]
    assert app.config["FB_APP_SECRET"]
    assert app.config["FB_HOURLY_RATELIMIT"]
    assert app.config["FB_BATCH_SIZE"]
    assert app.config["URL_BATCH_SIZE"]
