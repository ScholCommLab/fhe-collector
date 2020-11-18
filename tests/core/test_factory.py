# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test factory."""
import os
from app.main import create_app
import pytest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


def test_config_development():
    app = create_app("development")
    assert not app.config["TESTING"]
    assert not app.testing
    if os.getenv("TRAVIS") or False:
        assert app.config["TRAVIS"] is True
    else:
        assert app.config["TRAVIS"] is False
    assert app.config["DEBUG"] is True
    assert app.config["SECRET_KEY"] == "my-secret-key"
    assert (
        "postgresql://localhost/fhe_collector_dev"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert not app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]
    assert "API_TOKEN" in app.config
    assert app.config["API_TOKEN"] is None
    assert app.config["ADMIN_EMAIL"] is None
    assert app.config["APP_EMAIL"] is None
    assert app.config["NCBI_TOOL"] is None
    assert app.config["FB_APP_ID"] is None
    assert app.config["FB_APP_SECRET"] is None
    assert app.config["FB_HOURLY_RATELIMIT"] == 200
    assert app.config["FB_BATCH_SIZE"] == 50
    assert app.config["URL_BATCH_SIZE"] == 1000
    assert "fhe_collector" == app.name


def test_config_testing():
    app = create_app("testing")
    assert "TESTING" in app.config
    assert app.config["TESTING"]
    assert app.testing
    if os.getenv("TRAVIS") or False:
        assert app.config["TRAVIS"] is True
    else:
        assert app.config["TRAVIS"] is False
    assert app.config["DEBUG"] is False
    assert app.config["SECRET_KEY"] == "secret-env-key"
    assert (
        "postgresql://localhost/fhe_collector_test"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "SQLALCHEMY_ECHO" in app.config
    assert not app.config["SQLALCHEMY_ECHO"]
    assert app.config["API_TOKEN"] == "api-token"
    assert app.config["ADMIN_EMAIL"] == "admin@fhe.com"
    assert app.config["APP_EMAIL"] == "app@fhe.com"
    assert app.config["NCBI_TOOL"] == "FHE Collector"
    assert app.config["FB_APP_ID"] == "123456789012345"
    assert app.config["FB_APP_SECRET"] == "0987654321"
    assert app.config["FB_HOURLY_RATELIMIT"] == 100
    assert app.config["FB_BATCH_SIZE"] == 20
    assert app.config["URL_BATCH_SIZE"] == 500
    assert "fhe_collector" == app.name


def test_config_travis():
    app = create_app("travis")
    assert "TESTING" in app.config
    assert app.config["TESTING"]
    assert app.testing
    assert app.config["TRAVIS"] is True
    assert app.config["DEBUG"] is False
    assert (
        "postgresql+psycopg2://postgres@localhost:5432/travis_ci_test"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "SQLALCHEMY_ECHO" in app.config
    assert "fhe_collector" == app.name


def test_config_production():
    app = create_app("production")
    assert "TESTING" in app.config
    assert not app.config["TESTING"]
    assert not app.testing
    if os.getenv("TRAVIS") or False:
        assert app.config["TRAVIS"] is True
    else:
        assert app.config["TRAVIS"] is False
    assert app.config["DEBUG"] is False
    assert app.config["SECRET_KEY"] == "my-secret-key"
    assert (
        "postgresql://localhost/fhe_collector" == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "fhe_collector" == app.name
