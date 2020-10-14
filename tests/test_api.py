# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test API."""
from flask import request, jsonify
from json import loads


def api_add_data_response():
    response = {"api_version": "1.0", "status": "on"}
    return response


def test_homepage_url(client):
    """Start with a blank database."""

    rv = client.get("/api")
    assert 200 == rv.status_code

    rv = client.get("/api/v1")
    assert 200 == rv.status_code


def test_add_data_url(client):
    """Start with a blank database."""

    rv = client.get("/api/v1/add_data")
    assert 200 == rv.status_code
    print(rv.data)
    assert api_add_data_response() == loads(rv.data)
