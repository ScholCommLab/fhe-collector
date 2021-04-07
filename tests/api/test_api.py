# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test API."""
from json import loads

from flask import jsonify
from flask import request


def api_add_data_response():
    response = {"api_version": "1.0", "status": "on"}
    return response


def test_api(client):
    """Start with a blank database."""

    rv = client.get("/api/")
    assert 200 == rv.status_code


def test_v1(client):
    """Start with a blank database."""

    rv = client.get("/api/v1/")
    assert 200 == rv.status_code


# def test_add_data(client):
#     """Start with a blank database."""
#
#     rv = client.get("/api/v1/add_data")
#     assert 200 == rv.status_code
#     assert api_add_data_response() == loads(rv.data)
#
#     response = client.post(
#         '/api/v1/add_data',
#         data={"doi": "10.22230/src.2014v5n2a172", "url": "http://src-online.ca/index.php/src/article/view/172", "url_type": "ojs"},
#         headers={"X-API-Key": client.config["API_TOKEN"]}
#     )
#     assert 'http://localhost/auth/login' == response.headers['Location']
