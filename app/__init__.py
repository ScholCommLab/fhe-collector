"""
.. module::
    :platform: Linux
    :synopsis: Web-app to collect facebook metrics.

.. moduleauthor:: Stefan Kasberger <mail@stefankasberger.at>
"""


from apscheduler.schedulers.background import BackgroundScheduler
import csv
from datetime import datetime
from facebook import GraphAPI
from json import dumps, loads
import logging
from logging.handlers import RotatingFileHandler
import os
import pandas as pd
from psycopg2 import connect
import re
import requests
import urllib.parse
from tqdm import tqdm
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import create_engine
from app.models import Doi
from app.models import FBRequest
from app.models import Url


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

db = SQLAlchemy()
migrate = Migrate()


def import_dois_from_csv(filename):
    """Import DOI's from a csv file.

    Imports the DOI's from a csv file into the database. It must contain an
    attribute `doi`, and optionally `url`, `url_type` and `date`.
    For development purposes there is a file with 100 entries you can use.

    Parameters
    ----------
    filename : string
        Filepath for the csv file.

    Returns
    -------
    bool
        True, if import worked, False if not.

    """
    from app.models import Import

    try:
        df = pd.read_csv(filename, encoding='utf8', parse_dates=True)
        df = df.drop_duplicates(subset='doi')
        data = df.to_json(orient='records')
        imp = Import('<file '+filename+'>', data)
        db.session.add(imp)
        db.session.commit()
        store_data_to_database(loads(data), imp.id)
        return True
    except:
        print('Error: CSV file for import not working.')
        return False


def import_dois_from_api(data):
    """Import data coming from the API endpoint.

    Parameters
    ----------
    data : type
        Description of parameter `data`.

    Returns
    -------
    string
        Response text for API request.

    """
    from app.models import Import

    try:
        imp = Import('<api>', dumps(data))
        db.session.add(imp)
        db.session.commit()
        response = store_data_to_database(data, imp.id)
        return response
    except:
        response = 'Error: Data import from API not working'
        return response


def validate_doi(doi):
    """Validate a DOI via RegEx.

    Parameters
    ----------
    doi : string
        A single DOI to be validated.

    Returns
    -------
    bool
        True, if DOI is valid, False if not.

    """
    # validate doi
    patterns = [
        r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$",
        r"^10.1002/[^\s]+$",
        r"^10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d$",
        r"^10.1021/\w\w\d+$",
        r"^10.1207\/[\w\d]+\&\d+_\d+$"
    ]
    is_valid = False
    for pat in patterns:
        if re.match(pat, doi, re.IGNORECASE):
            is_valid = True
    return is_valid


def store_data_to_database(data, import_id):
    """Store data to database.

    Parameters
    ----------
    data : list
        List of dictionaries.
    import_id : string
        Id of Import() table, where the raw data was stored in.

    Returns
    -------
    dict
        Import metrics as dict(). Keys: 'doi_list', 'dois_added',
        'dois_already_in', 'urls_added', 'urls_already_in'

    """
    from app.models import Doi
    from app.models import Url

    dois_added = 0
    dois_already_in = 0
    urls_added = 0
    urls_already_in = 0
    doi_list = []

    for entry in tqdm(data):
        is_valid = validate_doi(entry['doi'])
        # TODO: what if not valid? user does not get it back in the api response.
        if is_valid:
            result_doi = Doi.query.filter_by(doi=entry['doi']).first()
            if result_doi is None:
                doi = Doi(
                    doi=entry['doi'],
                    import_id=import_id
                )
                db.session.add(doi)
                dois_added += 1
            else:
                doi = result_doi
                dois_already_in += 1
            # store url
            if entry['url']:
                result_url = Url.query.filter_by(url=entry['url']).first()
                if result_url is None:
                    url = Url(
                        url=entry['url'],
                        doi=str(doi.doi),
                        url_type='ojs'
                    )
                    db.session.add(url)
                    urls_added += 1
                else:
                    urls_already_in += 1
            db.session.commit()
        doi_list.append(entry['doi'])

    print(dois_added, 'doi\'s added to database.')
    print(dois_already_in, 'doi\'s already in database.')
    print(urls_added, 'url\'s added to database.')
    print(urls_already_in, 'url\'s already in database.')

    return {'doi_list': doi_list, 'dois_added': dois_added, 'dois_already_in': dois_already_in, 'urls_added': urls_added, 'urls_already_in': urls_already_in}


def create_doi_urls():
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    from app.models import Doi
    from app.models import Url

    urls_new_added = 0
    urls_new_already_in = 0
    urls_old_added = 0
    urls_old_already_in = 0
    urls_landingpage_added = 0
    urls_landingpage_already_in = 0

    result_doi = Doi.query.all()
    for row in tqdm(result_doi):
        doi_url_encoded = urllib.parse.quote(row.doi)
        # always overwrite the url at the beginning of each section
        # create new doi url
        url = 'https://doi.org/{0}'.format(doi_url_encoded)
        result_url = Url.query.filter_by(url=url).first()
        if result_url is None:
            url = Url(
                url=url,
                doi=row.doi,
                url_type='doi_new'
            )
            db.session.add(url)
            urls_new_added += 1
        else:
            urls_new_already_in += 1

        # create old doi url
        url = 'http://dx.doi.org/{0}'.format(doi_url_encoded)
        result_url = Url.query.filter_by(url=url).first()
        if result_url is None:
            url = Url(
                url=url,
                doi=row.doi,
                url_type='doi_old'
            )
            db.session.add(url)
            urls_old_added += 1
        else:
            urls_old_already_in += 1

        # create doi landing page url
        url = 'https://doi.org/{0}'.format(doi_url_encoded)
        resp = requests.get(url, allow_redirects=True)
        url = resp.url
        result_url = Url.query.filter_by(url=url).first()
        if result_url is None:
            url = Url(
                url=url,
                doi=row.doi,
                url_type='doi_landingpage'
            )
            db.session.add(url)
            urls_landingpage_added += 1
        else:
            urls_landingpage_already_in += 1
        db.session.commit()
    print(urls_new_added, 'doi new url\'s added to database.')
    print(urls_new_already_in, 'doi new url\'s already in database.')
    print(urls_old_added, 'doi old url\'s added to database.')
    print(urls_old_already_in, 'doi old url\'s already in database.')
    print(urls_landingpage_added,
          'doi new landing page url\'s added to database.')
    print(urls_landingpage_already_in,
          'doi new landing page url\'s already in database.')


def create_ncbi_urls(ncbi_tool, email):
    """Create NCBI URL's from the identifier.

    https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/

    Parameters
    ----------
    ncbi_tool : string
        Name of tool, which want to connect to the NCBI API.
    email : string
        Email related to the app, used as credential for the request.

    """
    from app.models import Doi
    from app.models import Url

    urls_pm_added = 0
    urls_pm_already_in = 0
    urls_pmc_added = 0
    urls_pmc_already_in = 0

    result_doi = Doi.query.all()

    for row in tqdm(result_doi):
        # TODO: allows up to 200 ids sent at the same time
        # send request to NCBI API
        doi_url_encoded = urllib.parse.quote(row.doi)
        url = ' https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={0}'.format(doi_url_encoded)
        resp = requests.get(url, params={
            'tool': ncbi_tool,
            'email': email,
            'idtype': 'doi', 'versions': 'no', 'format': 'json'})
        resp = resp.json()
        if 'records' in resp:
            # create PMC url
            if 'pmcid' in resp['records']:
                url = 'https://ncbi.nlm.nih.gov/pmc/articles/PMC{0}/'.format(
                    resp['records']['pmcid'])
                result_url = Url.query.filter_by(url=url).first()
                if result_url is None:
                    url = Url(
                        url=url,
                        doi=row.doi,
                        url_type='pmc'
                    )
                    db.session.add(url)
                    urls_pmc_added += 1
                else:
                    urls_pmc_already_in += 1
            # create PM url
            if 'pmid' in resp['records']:
                url = 'https://www.ncbi.nlm.nih.gov/pubmed/{0}'.format(
                    resp['records']['pmid'])
                result_url = Url.query.filter_by(url=url).first()
                if result_url is None:
                    url = Url(
                        url=url,
                        doi=row.doi,
                        url_type='pm'
                    )
                    db.session.add(url)
                    urls_pm_added += 1
                else:
                    urls_pm_already_in += 1
        db.session.commit()

    print(urls_pm_added, 'PM url\'s added to database.')
    print(urls_pm_already_in, 'PM url\'s already in database.')
    print(urls_pmc_added, 'PMC url\'s added to database.')
    print(urls_pmc_already_in, 'PMC url\'s already in database.')


def create_unpaywall_urls(email):
    """Create Unpaywall URL's from the identifier.

    https://unpaywall.org/products/api

    Parameters
    ----------
    email : string
        Email related to the app, used as credential for the request.

    """
    from app.models import Doi
    from app.models import Url

    urls_unpaywall_added = 0
    urls_unpaywall_already_in = 0

    result_doi = Doi.query.all()

    for row in tqdm(result_doi):
        # send request to Unpaywall API
        url_dict = {}
        doi_url_encoded = urllib.parse.quote(row.doi)
        url = 'https://api.unpaywall.org/v2/{0}?email={1}'.format(doi_url_encoded, ncbi_email)
        resp = requests.get(url)
        resp = resp.json()
        # check if response includes needed data
        if 'doi_url' in resp:
            url_dict['unpaywall_doi_url'] = resp['doi_url']
        if 'oa_locations' in resp:
            for loc in resp['oa_locations']:
                if 'url_for_pdf' in loc:
                    if loc['url_for_pdf']:
                        url_dict['unpaywall_url_for_pdf'] = loc['url_for_pdf']
                if 'url' in loc:
                    if loc['url']:
                        url_dict['unpaywall_url'] = loc['url']
                if 'url_for_landing_page' in loc:
                    if loc['url_for_landing_page']:
                        url_dict['unpaywall_url_for_landing_page'] = loc['url_for_landing_page']

        # store URL's in database
        for url_type, url in url_dict.items():
            result_url = Url.query.filter_by(url=url).first()
            if result_url is None:
                url = Url(
                    url=url,
                    doi=row.doi,
                    url_type=url_type
                )
                db.session.add(url)
                urls_unpaywall_added += 1
            else:
                urls_unpaywall_already_in += 1
        db.session.commit()

    print(urls_unpaywall_added, 'Unpaywall url\'s added to database.')
    print(urls_unpaywall_already_in, 'Unpaywall url\'s already in database.')


def fb_requests(app_id, app_secret):
    """Get app access token.

    {'id': 'http://dx.doi.org/10.22230/src.2010v1n2a24',
    'engagement': { 'share_count': 0, 'comment_plugin_count': 0,
                    'reaction_count': 0, 'comment_count': 0}}
    """
    from app.models import FBRequest

    # TODO: for what extended_user_access function? https://github.com/ScholCommLab/fhe-plos/blob/master/code/2_collect_private.py

    payload = {'grant_type': 'client_credentials',
               'client_id': app_id,
               'client_secret': app_secret}
    try:
        response = requests.post(
            'https://graph.facebook.com/oauth/access_token?',
            params=payload)
    except requests.exceptions.RequestException:
        raise Exception()

    token = json.loads(response.text)
    fb_graph = GraphAPI(token['access_token'], version="2.10")

    fb_request_added = 0
    result_url = Url.query.all()
    for row in result_url:
        try:
            url = row.url
            result = fb_graph.get_object(id=url, fields="engagement,og_object")
            err_msg = None
        except Exception as e:
            err_msg = str(e)
            print(e)
            result = None

        if result:
            fb_request = FBRequest(
                url=row.url,
                response=result
            )
            db.session.add(fb_request)
            fb_request_added += 1
    db.session.commit()
    print(fb_request_added, 'Facebook openGraph Request\'s added to database.')


def delete_dois():
    """Delete all doi entries."""
    from app.models import Doi
    try:
        dois_deleted = db.session.query(Doi).delete()
        db.session.commit()
        print(dois_deleted, 'doi\'s deleted from database.')
    except:
        db.session.rollback()
        print('ERROR: Doi\'s can not be deleted from database.')


def delete_urls():
    """Delete all url entries."""
    from app.models import Url
    try:
        urls_deleted = db.session.query(Url).delete()
        db.session.commit()
        print(urls_deleted, 'url\'s deleted from database.')
    except:
        db.session.rollback()
        print('ERROR: Url\'s can not be deleted from database.')


def delete_fbrequests():
    """Delete all facebook requests."""
    from app.models import FBRequest
    try:
        fbrequests_deleted = db.session.query(FBRequest).delete()
        db.session.commit()
        print(fbrequests_deleted, 'FBRequests\'s deleted from database.')
    except:
        db.session.rollback()
        print('ERROR: Facebook requests\'s can not be deleted from database.')


def export_tables_to_csv(table_names, db_uri):
    """Short summary.

    Parameters
    ----------
    table_names : list
        Description of parameter `table_names`.
    db_uri : string
        Description of parameter `db_uri`.

    """
    con = connect(db_uri)
    cur = con.cursor()
    filename_list = [BASE_DIR + '/app/static/export/'+datetime.today().strftime('%Y-%m-%d')+'_'+table+'.csv' for table in table_names]

    for idx, filename in enumerate(filename_list):
        sql = "COPY "+table_names[idx]+" TO STDOUT DELIMITER ',' CSV HEADER;"
        cur.copy_expert(sql, open(filename, "w"))


def import_tables_from_csv(table_names, db_uri, mode='overwrite'):
    """Insert data from csv files into tables.

    naming conventions for files: TABLENAME.csv
    TABLENAME: `doi`, `fb_request` and `url`

    No duplicates allowed!

    """
    # TODO: Add data to Import()
    filename_list = [BASE_DIR + '/app/static/import/'+table+'.csv' for table in table_names]
    table2model = {
        'doi': Doi,
        'fb_request': FBRequest,
        'url': Url
    }

    for idx, filename in enumerate(filename_list):
        model = table2model[table_names[idx]]
        df = pd.read_csv(filename)
        for row in df.to_dict(orient="records"):
            if table_names[idx] == 'doi':
                model = Doi(**row)
            if table_names[idx] == 'url':
                model = Url(**row)
            if table_names[idx] == 'fb_request':
                model = FBRequest(**row)
            db.session.add(model)
    db.session.commit()


def create_app():
    """Create application and load settings."""
    app = Flask(__name__)

    ENVIRONMENT = os.getenv('ENV', default='development')
    # TESTING = os.getenv('TESTING', default=False)
    print('* Updating App Mode to: ' + ENVIRONMENT)
    travis = os.getenv('TRAVIS', default=False)
    if not travis:
        print('* Loading User Settings.')
        app.config.from_pyfile(BASE_DIR+'/settings_user.py', silent=True)
    if ENVIRONMENT == 'development':
        print('* Loading Development Settings.')
        app.config.from_pyfile(BASE_DIR+'/settings_development.py', silent=True)
        app.config.from_object('settings_default.Development')
        if not travis:
            DebugToolbarExtension(app)
    elif ENVIRONMENT == 'production':
        print('* Loading Production Settings.')
        # order of settings loading: 1. settings file, 2. environment variable DATABASE_URL, 3. environment variable SQLALCHEMY_DATABASE_URI
        if not travis:
            app.config.from_pyfile(BASE_DIR+'/settings_production.py', silent=True)
        app.config.from_object('settings_default.Production')
    elif ENVIRONMENT == 'testing':
        print('* Loading Test Settings.')
        app.config['TESTING'] = True
        app.config.from_object('settings_default.Testing')
    if not travis:
        print('* Database: ' + app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)
    migrate.init_app(app, db)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(hello_job, trigger='interval', seconds=3)
    # scheduler.start()

    if not app.debug and not app.testing:

        # Logging (only production)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/fhe.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Facebook Hidden Engagement')

    return app


from app import models
