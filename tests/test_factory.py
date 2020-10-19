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
            "SECRET_KEY": "secret-dev-key",
            "TESTING": False,
            "TRAVIS": False,
        }
    )
    assert "FLASK_ENV" in app.config
    assert "APP_SETTINGS" not in app.config
    assert "TESTING" in app.config
    assert not app.config["TESTING"]
    assert not app.testing
    assert "TRAVIS" in app.config
    assert not app.config["TRAVIS"]
    assert "DEBUG" in app.config
    assert app.config["DEBUG"]
    assert "secret-dev-key" == app.config["SECRET_KEY"]
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert (
        "postgresql://localhost/fhe_collector" == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert not app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]
    assert "fhe_collector" == app.name


def test_config_development_app_settings():
    app = create_app(
        {
            "FLASK_ENV": "development",
            "SECRET_KEY": "secret-dev-key",
            "APP_SETTINGS": "settings_testing.json",
            "TESTING": False,
            "TRAVIS": False,
        }
    )
    assert "FLASK_ENV" in app.config
    assert "APP_SETTINGS" in app.config
    assert "settings_testing.json" in app.config["APP_SETTINGS"]
    assert "TESTING" in app.config
    assert not app.config["TESTING"]
    assert not app.testing
    assert "TRAVIS" in app.config
    assert not app.config["TRAVIS"]
    assert "DEBUG" in app.config
    assert app.config["DEBUG"]
    assert "secret-dev-key" == app.config["SECRET_KEY"]
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert (
        "postgresql://localhost/fhe_collector" == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert not app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]
    assert "API_TOKEN" in app.config
    assert isinstance(app.config["API_TOKEN"], str)
    assert "CSV_FILENAME" in app.config
    assert isinstance(app.config["CSV_FILENAME"], str)
    assert "ADMIN_EMAIL" in app.config
    assert isinstance(app.config["ADMIN_EMAIL"], str)
    assert "APP_EMAIL" in app.config
    assert isinstance(app.config["APP_EMAIL"], str)
    assert "NCBI_TOOL" in app.config
    assert isinstance(app.config["NCBI_TOOL"], str)
    assert "FB_APP_ID" in app.config
    assert isinstance(app.config["FB_APP_ID"], str)
    assert "FB_APP_SECRET" in app.config
    assert isinstance(app.config["FB_APP_SECRET"], str)
    assert "FB_HOURLY_RATELIMIT" in app.config
    assert isinstance(app.config["FB_HOURLY_RATELIMIT"], int)
    assert "FB_BATCH_SIZE" in app.config
    assert isinstance(app.config["FB_BATCH_SIZE"], int)
    assert "URL_BATCH_SIZE" in app.config
    assert isinstance(app.config["URL_BATCH_SIZE"], int)
    assert "fhe_collector" == app.name


def test_config_testing():
    app = create_app(
        {"SECRET_KEY": "secret-testing-key", "TESTING": True, "TRAVIS": False}
    )
    assert "FLASK_ENV" not in app.config
    assert "APP_SETTINGS" not in app.config
    assert "TESTING" in app.config
    assert app.config["TESTING"]
    assert "TRAVIS" in app.config
    assert not app.config["TRAVIS"]
    assert app.testing
    assert "DEBUG" in app.config
    assert app.config["DEBUG"]
    assert "secret-testing-key" == app.config["SECRET_KEY"]
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert (
        "postgresql://localhost/fhe_collector_test"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "SQLALCHEMY_ECHO" in app.config
    assert not app.config["SQLALCHEMY_ECHO"]
    assert "fhe_collector" == app.name


def test_config_testing_travis():
    app = create_app(
        {"SECRET_KEY": "secret-travis-key", "TESTING": True, "TRAVIS": True}
    )
    assert "FLASK_ENV" not in app.config
    assert "APP_SETTINGS" not in app.config
    assert "TESTING" in app.config
    assert app.config["TESTING"]
    assert app.testing
    assert "TRAVIS" in app.config
    assert app.config["TRAVIS"]
    assert "DEBUG" in app.config
    assert app.config["DEBUG"]
    assert "secret-travis-key" == app.config["SECRET_KEY"]
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert (
        "postgresql+psycopg2://postgres@localhost:5432/travis_ci_test"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "SQLALCHEMY_ECHO" in app.config
    assert "fhe_collector" == app.name


def test_config_production():
    app = create_app(
        {
            "FLASK_ENV": "production",
            "SECRET_KEY": "secret-prod-key",
            "TESTING": False,
            "TRAVIS": False,
            "DEBUG": False,
        }
    )
    assert "FLASK_ENV" in app.config
    assert "APP_SETTINGS" not in app.config
    assert "TESTING" in app.config
    assert not app.config["TESTING"]
    assert not app.testing
    assert "TRAVIS" in app.config
    assert not app.config["TRAVIS"]
    assert "DEBUG" in app.config
    assert not app.config["DEBUG"]
    assert "secret-prod-key" == app.config["SECRET_KEY"]
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert (
        "postgresql://localhost/fhe_collector" == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "fhe_collector" == app.name
