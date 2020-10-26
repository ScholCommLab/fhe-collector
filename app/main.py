from flask import Blueprint
from flask import render_template

bp = Blueprint("main", __name__)


@bp.route("/")
@bp.route("/index")
def index():
    """Homepage."""
    return render_template("index.html", title="Home")
