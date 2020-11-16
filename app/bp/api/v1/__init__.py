# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""API functions."""
from flask import request, Blueprint


blueprint = Blueprint("v1", __name__)


@blueprint.route("/")
def index():
    return {"path": "add_data/", "name": "add_data"}


@blueprint.route("/add_data", methods=["POST"])
def add_data():
    """Add data via an API endpoint to the database.

    Required: doi
    Optional: url, date
    """
    # TODO: merge with index or remove /add_data url from blueprint
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

    json_data = request.get_json()
    # token = json_data["token"]

    if request.method == "POST":
        try:
            if "X-API-Key" in request.headers:
                if app.config["API_TOKEN"] == request.headers["X-API-Key"]:
                    if request.headers["Content-Type"] == "application/json":
                        json_data = request.get_json()
                        if isinstance(json_data, list):
                            is_data_valid = True
                            for entry in data:
                                # Validate entry
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
                                    else:
                                        print("URL is missing")
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
                                        response = "Date is missing."
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
