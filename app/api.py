# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""API functions."""
from flask import Blueprint
from flask import render_template
from flask import request
from flask import jsonify


bp = Blueprint("api", __name__)


@bp.route("/api")
@bp.route("/api/v1")
def api():
    """Api page."""
    return render_template("api.html", title="API")


@bp.route("/api/v1/add_data", methods=["POST", "GET"])
def add_data():
    """Add data via an API endpoint to the database.

    Required: doi
    Optional: url, date
    """
    response_status = "error"
    url_type_list = [
        "ojs",
        "doi_new",
        "doi_old",
        "doi_new_landingpage",
        "unpaywall",
        "pubmed",
        "pubmedcentral",
    ]

    if request.method == "POST":
        try:
            if "X-API-Key" in request.headers:
                if app.config["API_TOKEN"] == request.headers["X-API-Key"]:
                    if request.headers["Content-Type"] == "application/json":
                        data = request.json
                        if isinstance(data, list):
                            is_data_valid = True
                            for entry in data:
                                if "doi" in entry:
                                    if not isinstance(entry["doi"], str):
                                        response = "DOI {} is no string.".format(
                                            entry["doi"]
                                        )
                                        is_data_valid = False
                                    if "url" in entry:
                                        if not isinstance(entry["url"], str):
                                            response = "URL {} is no string.".format(
                                                entry["url"]
                                            )
                                            is_data_valid = False
                                        if "url_type" in entry:
                                            if not isinstance(entry["url_type"], str):
                                                response = "URL type {} is no string.".format(
                                                    entry["url_type"]
                                                )
                                                is_data_valid = False
                                            if entry["url_type"] not in url_type_list:
                                                response = "URL type {} is not one of the allowed types.".format(
                                                    entry["url_type"]
                                                )
                                                is_data_valid = False
                                        else:
                                            response = "URL type is missing."
                                            is_data_valid = False
                                    if "date" in entry:
                                        if not isinstance(entry["date"], str):
                                            response = "Date {} is no string.".format(
                                                entry["date"]
                                            )
                                            is_data_valid = False
                                else:
                                    is_data_valid = False
                                    response = "DOI is missing in {}.".format(entry)
                            if is_data_valid:
                                resp_func = import_dois_from_api(data)
                                if resp_func:
                                    response = resp_func
                                    response_status = "ok"
                                else:
                                    response = "Error: JSON from API could not be stored in database."
                        else:
                            response = "No list of data in JSON."
                    else:
                        response = "No JSON delivered."
                else:
                    response = "Authentication token not right."
            else:
                response = "Authentication token not passed."
        except:
            response = "Undefined error."

        return jsonify({"status": response_status, "content": response})
    else:
        return jsonify({"status": "on", "api_version": "1.0"})
