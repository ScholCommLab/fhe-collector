# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test main."""


def test_homepage_url(client):
    """Start with a blank database."""

    rv = client.get("/")
    assert 200 == rv.status_code

    rv = client.get("/index")
    assert 200 == rv.status_code
