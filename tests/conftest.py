# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""conftest"""
import os
import tempfile
import pytest
from fhe_collector.database import init_db
from fhe_collector import create_app


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()

    # create the app with common test config
    if os.getenv("TRAVIS") or False:
        app = create_app("travis")
    else:
        app = create_app("testing")

    # create the database and load test data
    with app.app_context():
        init_db()

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
