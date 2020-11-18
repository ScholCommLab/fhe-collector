# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test database."""
import pytest
from app.db import get_db


def test_get_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()


def test_init_db(runner):
    result = runner.invoke(args=["init-db"])
    assert result
