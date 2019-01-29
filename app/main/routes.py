from flask import render_template
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')


@bp.route('/add_doi_url')
def add_doi_url():
    return render_template('index.html', title='Add DOI and URL')
