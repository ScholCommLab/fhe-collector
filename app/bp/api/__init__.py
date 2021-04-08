# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""API functions."""
from flask import Blueprint
from flask import jsonify


blueprint = Blueprint("api", __name__)


@blueprint.route("/")
def index() -> str:
    """Get API root."""
    return jsonify(
        [
            {
                "path": "/v1",
                "name": "v1",
                "version": "1.0.0",
                "major": 1,
                "minor": 0,
                "micro": 0,
                "release_date": "2020-11-16",
                "status": "online",
            }
        ]
    )
