# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test factory."""
import os
from app.main import create_app


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


def test_config_development(monkeypatch):

    for ele in range(2):
        if ele == 0:
            monkeypatch.setenv("FLASK_CONFIG", "development")
            monkeypatch.setenv("SECRET_KEY", "secret-test-key")
        elif ele == 1:
            monkeypatch.setenv("SECRET_KEY", "secret-test-key")
        app = create_app()

        assert app.config["FLASK_ENV"] == "development"
        assert app.config["DEBUG"] is True
        assert not app.testing
        assert not app.config["TESTING"]
        assert app.config["SECRET_KEY"] == "secret-test-key"
        assert isinstance(app.config["SQLALCHEMY_DATABASE_URI"], str)
        assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
        assert not app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]
        assert "fhe_collector" == app.name


def test_config_testing(monkeypatch):
    monkeypatch.setenv("FLASK_CONFIG", "testing")
    app = create_app()

    assert app.config["FLASK_DEBUG"] is False
    assert app.config["DEBUG"] is False
    assert app.testing
    assert app.config["TESTING"]
    assert app.config["SECRET_KEY"] == "secret-env-key"
    assert (
        "postgresql://localhost/fhe_collector_test"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "SQLALCHEMY_ECHO" in app.config
    assert not app.config["SQLALCHEMY_ECHO"]
    assert app.config["ADMIN_EMAIL"] == "admin@fhe.com"
    assert app.config["APP_EMAIL"] == "app@fhe.com"
    assert app.config["NCBI_TOOL"] == "FHE Collector"
    assert app.config["FB_API_TOKEN"] == "api-token"
    assert app.config["FB_APP_ID"] == "123456789012345"
    assert app.config["FB_APP_SECRET"] == "0987654321"
    assert app.config["FB_HOURLY_RATELIMIT"] == 100
    assert app.config["FB_BATCH_SIZE"] == 20
    assert app.config["URL_BATCH_SIZE"] == 500
    assert "fhe_collector" == app.name


def test_config_travis(monkeypatch):
    monkeypatch.setenv("FLASK_CONFIG", "testing")
    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://postgres@localhost:5432/travis_ci_test",
    )
    monkeypatch.setenv("TRAVIS", "true")
    app = create_app()

    assert app.config["TRAVIS"] is True
    assert app.config["FLASK_ENV"] == "testing"
    assert app.config["FLASK_DEBUG"] is False
    assert app.config["DEBUG"] is False
    assert not app.testing
    assert not app.config["TESTING"]
    assert app.config["SECRET_KEY"] == "secret-env-key"
    assert (
        "postgresql+psycopg2://postgres@localhost:5432/travis_ci_test"
        == app.config["SQLALCHEMY_DATABASE_URI"]
    )
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "SQLALCHEMY_ECHO" in app.config
    assert not app.config["SQLALCHEMY_ECHO"]
    assert app.config["ADMIN_EMAIL"] == "admin@fhe.com"
    assert app.config["APP_EMAIL"] == "app@fhe.com"
    assert app.config["NCBI_TOOL"] == "FHE Collector"
    assert app.config["FB_API_TOKEN"] == "api-token"
    assert app.config["FB_APP_ID"] == "123456789012345"
    assert app.config["FB_APP_SECRET"] == "0987654321"
    assert app.config["FB_HOURLY_RATELIMIT"] == 100
    assert app.config["FB_BATCH_SIZE"] == 20
    assert app.config["URL_BATCH_SIZE"] == 500
    assert "fhe_collector" == app.name


def test_config_production(monkeypatch):
    monkeypatch.setenv("FLASK_CONFIG", "production")
    app = create_app()

    assert app.config["FLASK_ENV"] == "production"
    assert not app.config["TESTING"]
    assert not app.testing
    assert app.config["FLASK_DEBUG"] is False
    assert app.config["DEBUG"] is False
    assert isinstance(app.config["SQLALCHEMY_DATABASE_URI"], str)
    assert not app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
    assert "DEBUG_TB_INTERCEPT_REDIRECTS" not in app.config
    assert "fhe_collector" == app.name
