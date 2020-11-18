# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""main functions."""
from flask import Blueprint
from flask import render_template, current_app
from flask_sqlalchemy import get_debug_queries

from app.db import get_db
from app.models import Doi, Import, Url, Request, FBRequest


blueprint = Blueprint("main", __name__)


@blueprint.route("/")
@blueprint.route("/index")
def index():
    """Homepage."""
    return render_template("index.html", title="Home")


@blueprint.route("/stats")
def stats():
    """Statistics."""
    db = get_db()
    data = {
        "imports": db.session.query(Import).count(),
        "dois": {
            "num": db.session.query(Doi).count(),
            "new": db.session.query(Doi).filter(Doi.url_doi_new == True).count(),
            "old": db.session.query(Doi).filter(Doi.url_doi_old == True).count(),
            "lp": db.session.query(Doi).filter(Doi.url_doi_lp == True).count(),
            "ncbi": db.session.query(Doi).filter(Doi.url_ncbi == True).count(),
            "pmc": db.session.query(Doi).filter(Doi.url_pmc == True).count(),
            "pm": db.session.query(Doi).filter(Doi.url_pm == True).count(),
            "unpaywall": db.session.query(Doi)
            .filter(Doi.url_unpaywall == True)
            .count(),
        },
        "urls": {
            "num": db.session.query(Url).count(),
            "new": db.session.query(Url).filter(Url.url_type == "doi_new").count(),
            "old": db.session.query(Url).filter(Url.url_type == "doi_old").count(),
            "lp": db.session.query(Url).filter(Url.url_type == "doi_lp").count(),
            "pm": db.session.query(Url).filter(Url.url_type == "pm").count(),
            "pmc": db.session.query(Url).filter(Url.url_type == "pmc").count(),
            "unpaywall": db.session.query(Url)
            .filter(Url.url_type == "unpaywall")
            .count(),
            "ojs": db.session.query(Url).filter(Url.url_type == "ojs").count(),
        },
        "requests": {
            "num": db.session.query(Request).count(),
            "lp": db.session.query(Request)
            .filter(Request.request_type == "doi_lp")
            .count(),
            "ncbi": db.session.query(Request)
            .filter(Request.request_type == "ncbi")
            .count(),
            "unpaywall": db.session.query(Request)
            .filter(Request.request_type == "unpaywall")
            .count(),
        },
        "fbrequests": db.session.query(FBRequest).count(),
    }
    return render_template("stats.html", title="Statistics", data=data)


@blueprint.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= 0.5:
            current_app.logger.warning(
                "Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n"
                % (query.statement, query.parameters, query.duration, query.context)
            )
    return response
