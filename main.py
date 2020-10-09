# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/ScholCommLab/fhe-collector.

Copyright 2018 Stefan Kasberger

Licensed under the MIT License.
"""
import click
from flask import jsonify
from flask import render_template
from flask import request
from app import create_app
from app.database import (
    import_init_csv,
    delete_urls,
    delete_dois,
    create_doi_old_urls,
    create_doi_new_urls,
    create_doi_lp_urls,
)

# from app.db import create_unpaywall_urls, create_doi_lp_urls, create_doi_new_urls, create_doi_old_urls, create_ncbi_urls, delete_urls, delete_requests, delete_fbrequests, delete_dois, import_dois_from_api, init_from_csv, export_tables_to_csv, import_csv
# from app.requests import requests, fb_requests

__author__ = "Stefan Kasberger"
__email__ = "mail@stefankasberger.at"
__copyright__ = "Copyright (c) 2018 Stefan Kasberger"
__license__ = "MIT License"
__version__ = "0.1.0"
__url__ = "https://github.com/ScholCommLab/fhe-collector"


app = create_app()
app.app_context().push()


@app.cli.command()
@click.argument("filename", type=click.Path(exists=True), required=False)
def init_data(filename=None):
    """Import raw data from csv file.

    The filepath can be manually passed with the argument `filename`.

    Parameters
    ----------
    filename : string
        Relative filepath to the csv file. Defaults to None, if not passed as an
        argument via the command line. Relative to root.

    """
    if not filename:
        filename = app.config["CSV_FILENAME"]
    batch_size = app.config["URL_BATCH_SIZE"]
    import_init_csv(filename, batch_size)


@app.cli.command()
def del_init():
    """Delete initialized data (DOI's and URL's)."""
    delete_urls()
    delete_dois()


@app.cli.command()
@click.argument("filename", type=click.Path(exists=True), required=False)
def res_init(filename=None):
    """Reset initialized data (DOI's and URL's)."""
    delete_urls()
    delete_dois()
    if not filename:
        filename = app.config["CSV_FILENAME"]
    batch_size = app.config["URL_BATCH_SIZE"]
    import_init_csv(filename, batch_size)


@app.cli.command()
def doi_urls():
    """Create the doi URL's."""
    create_doi_old_urls(app.config["URL_BATCH_SIZE"])
    create_doi_new_urls(app.config["URL_BATCH_SIZE"])


@app.cli.command()
def doi_new_urls():
    """Create the new doi URL's."""
    create_doi_new_urls(app.config["URL_BATCH_SIZE"])


@app.cli.command()
def doi_old_urls():
    """Create the old doi URL's."""
    create_doi_old_urls(app.config["URL_BATCH_SIZE"])


@app.cli.command()
def doi_lp_urls():
    """Create the doi landing page URL's."""
    create_doi_lp_urls()


@app.cli.command()
def ncbi_urls():
    """Create the NCBI URL's."""
    create_ncbi_urls(app.config["NCBI_TOOL"], app.config["APP_EMAIL"])


@app.cli.command()
def unpaywall_urls():
    """Create the Unpaywall URL's."""
    create_unpaywall_urls(app.config["APP_EMAIL"])


@app.cli.command()
def fbrequests():
    """Create the Facebook request."""
    fb_requests(
        app.config["FB_APP_ID"],
        app.config["FB_APP_SECRET"],
        app.config["FB_BATCH_SIZE"],
    )


@app.cli.command()
def del_dois():
    """Delete all entries in Doi table."""
    delete_dois()


@app.cli.command()
def del_urls():
    """Delete all entries in Url table."""
    delete_urls()


@app.cli.command()
def del_requests():
    """Delete all entries in Requests table."""
    delete_requests()


@app.cli.command()
def del_fbrequests():
    """Delete all entries in FBRequests table."""
    delete_fbrequests()


@app.cli.command()
def del_all_data():
    """Delete all entries in all tables."""
    delete_fbrequests()
    delete_requests()
    delete_urls()
    delete_dois()


@app.cli.command()
def res_data():
    """Reset all entries in all tables (delete + init + preprocessing)."""
    delete_fbrequests()
    delete_requests()
    delete_urls()
    delete_dois()
    init_from_csv(app.config["CSV_FILENAME"], app.config["URL_BATCH_SIZE"])
    create_doi_old_urls(app.config["URL_BATCH_SIZE"])
    create_doi_new_urls(app.config["URL_BATCH_SIZE"])


@app.cli.command()
@click.argument("table_names", required=False)
def exp_tables(table_names):
    """Export tables passed as string, seperated by comma.

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    if not table_names:
        table_names = "doi,url,api_request,fb_request"

    table_names = table_names.split(",")
    export_tables_to_csv(table_names, app.config["SQLALCHEMY_DATABASE_URI"])


@app.cli.command()
@click.argument("table_names", required=False)
def imp_tables(table_names, delete_tables=False):
    """Import data.

    table_names must be passed in the right order.
    e.g. 'doi,url,api_request,fb_request'

    Files must be available as:
        fb_request.csv, api_request.csv, doi.csv, url.csv

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    if not table_names or table_names == "":
        table_names = ["doi", "url", "api_request", "fb_request"]
    else:
        table_names_tmp = [table_name.strip() for table_name in table_names.split(",")]
        table_names = table_names_tmp

    import_csv(table_names, delete_tables)


@app.route("/")
@app.route("/index")
def index():
    """Homepage."""
    return render_template("index.html", title="Home")


@app.route("/api")
@app.route("/api/v1")
def api():
    """Api page."""
    return render_template("api.html", title="API")


@app.route("/api/v1/add_data", methods=["POST", "GET"])
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


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Doi": Doi, "Url": Url}
