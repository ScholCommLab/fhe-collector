from flask import render_template

from app.db import get_db


def not_found_error(error):
    return render_template("404.html"), 404


def internal_error(error):
    db = get_db()
    db.session.rollback()
    return render_template("500.html"), 500
