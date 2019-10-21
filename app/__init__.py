"""
.. module::
    :platform: Linux
    :synopsis: Web-app to collect facebook metrics.

.. moduleauthor:: Stefan Kasberger <mail@stefankasberger.at>
"""

__author__ = 'Stefan Kasberger'
__email__ = 'stefan.kasberger@univie.ac.at'
__copyright__ = 'Copyright (c) 2019 Stefan Kasberger'
__license__ = 'MIT License'
__version__ = '0.0.1'
__url__ = 'https://github.com/ScholCommLab/fhe-collector'


# from apscheduler.schedulers.background import BackgroundScheduler
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
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from tqdm import tqdm
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

db = SQLAlchemy()
migrate = Migrate()


def validate_doi(doi):
    """Validate a DOI via regular expressions.

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


def init_from_csv(filename, batch_size):
    """Import DOI's from a csv file.

    Imports the DOI's from a csv file into the database. Stores the raw data
    and adds dois in table.also the It must contain an
    attribute `doi`, and optionally `url`, `url_type` and `date`.
    For test purposes, there is a file with 100 entries you can use.
    Checks, if duplicate dois are in the file and removes them.

    Parameters
    ----------
    filename : string
        Filepath for the csv file, relative from the root dir.

    Returns
    -------
    bool
        True, if import worked, False if not.

    """
    from app.models import Doi
    from app.models import Import
    from app.models import Url
    from app import db

    num_dois_added = 0
    num_urls_added = 0
    dois_added = []
    url_import_lst = []
    url_list = []

    filename = '{0}/{1}'.format(BASE_DIR, filename)
    df = pd.read_csv(filename, encoding='utf8')
    df = df.drop_duplicates(subset='doi')
    df = df.fillna(False)
    data = df.to_json(orient='records')

    try:
        db_imp = Import('<Init '+filename+'>', data)
        db.session.add(db_imp)
        db.session.commit()
    except:
        print('ERROR: Import() can not be stored in Database.')
        return False

    for i in range(0, len(df), batch_size):
        for _, row in tqdm(df[i:i+batch_size].iterrows()):
            dict_tmp = {}
            is_valid = validate_doi(row['doi'])
            if is_valid:
                if row['doi'] and row['date']:
                    db_doi = None
                    try:
                        db_doi = Doi(
                            doi=row['doi'],
                            date_published=datetime.strptime(row['date'], '%Y-%m-%d'),
                            import_id=db_imp.id,
                            is_valid=True
                            )
                        db.session.add(db_doi)
                        num_dois_added += 1
                        dois_added.append(row['doi'])
                    except:
                        print('ERROR: Can not import Doi {0}.'.format(row['doi']))
                    if row['url'] and row['url_type'] and db_doi:
                        if row['url'] not in url_list:
                            url_list.append(row['url'])
                            dict_tmp['doi'] = db_doi.doi
                            dict_tmp['url'] = row['url']
                            dict_tmp['url_type'] = row['url_type']
                            url_import_lst.append(dict_tmp)
                else:
                    print('WARNING: Entry {0} is not valid'.format(row['doi']))
            else:
                print('WARNING: DOI {} is not valid.'.format(row['doi']))
        db.session.commit()

    for i in range(0, len(url_import_lst), batch_size):
        for d in url_import_lst[i:i+batch_size]:
            try:
                db_url = Url(
                    url=d['url'],
                    doi=d['doi'],
                    url_type=d['url_type']
                )
                db.session.add(db_url)
                num_urls_added += 1
            except:
                print('ERROR: Can not import Url {0}.'.format(d['url']))
        db.session.commit()
    db.session.close()
    print('{0} doi\'s added to database.'.format(num_dois_added))
    print('{0} url\'s added to database.'.format(num_urls_added))

    return {'dois_added': dois_added, 'num_dois_added': num_dois_added, 'num_urls_added': num_urls_added}


def add_entries_to_database(data, import_id):
    """Store data to table Doi and Url.

    Parameters
    ----------
    data : list
        List of dictionaries.
    import_id : string
        Id of ``Import()`` table, where the raw data was stored in.

    Returns
    -------
    dict
        Import metrics as ``dict``. Keys: ``doi_list``, ``dois_added``,
        ``dois_already_in``, ``urls_added`` and ``urls_already_in``.

    """
    from app.models import Doi
    from app.models import Url

    num_dois_added = 0
    num_urls_added = 0
    dois_added = []
    url_import_lst = []
    url_list = []

    for entry in tqdm(data):
        dict_tmp = {}
        is_valid = validate_doi(entry['doi'])
        if is_valid:
            db_doi = None
            result_doi = Doi.query.filter_by(doi=entry['doi']).first()
            if result_doi is None:
                try:
                    db_doi = Doi(
                        doi=entry['doi'],
                        date_published=datetime.strptime(entry['date'], '%Y-%m-%d'),
                        import_id=import_id,
                        is_valid=True
                        )
                    db.session.add(db_doi)
                    num_dois_added += 1
                    dois_added.append(entry['doi'])
                    db.session.commit()
                except:
                    print('ERROR: Can not import Doi {0}.'.format(entry['doi']))
                if entry['url'] and entry['url_type'] and db_doi:
                    if entry['url'] not in url_list:
                        url_list.append(entry['url'])
                        dict_tmp['doi'] = db_doi.doi
                        dict_tmp['url'] = entry['url']
                        dict_tmp['url_type'] = entry['url_type']
                        url_import_lst.append(dict_tmp)
            else:
                print('WARNING: Entry {0} is not valid'.format(entry['doi']))
        else:
            print('WARNING: DOI {} is not valid.'.format(entry['doi']))
    db.session.commit()

    for d in url_import_lst:
        try:
            db_url = Url(
                url=d['url'],
                doi=d['doi'],
                url_type=d['url_type']
            )
            db.session.add(db_url)
            num_urls_added += 1
        except:
            print('ERROR: Can not import Url {0}.'.format(d['url']))
    db.session.commit()
    db.session.close()
    print('{0} doi\'s added to database.'.format(num_dois_added))
    print('{0} url\'s added to database.'.format(num_urls_added))

    return {'dois_added': dois_added, 'num_dois_added': num_dois_added, 'num_urls_added': num_urls_added}

    for entry in tqdm(data):
        is_valid = validate_doi(entry['doi'])
        # TODO: what if not valid? user does not get it back in the api response.
        if is_valid:
            if entry['doi'] and entry['date']:
                doi = entry['doi']
                result_doi = Doi.query.filter_by(doi=doi).first()
                if result_doi is None:
                    try:
                        db_doi = Doi(
                            doi=doi,
                            date_published=datetime.strptime(entry['date'], '%Y-%m-%d'),
                            import_id=import_id,
                            is_valid=True
                        )
                        db.session.add(db_doi)
                        db.session.commit()
                        num_dois_added += 1
                        dois_added.append(doi)
                    except:
                        print('ERROR: Can not import Doi {0}.'.format(doi))
                else:
                    doi = result_doi.doi
            else:
                print('WARNING: Entry {0} is not valid'.format(doi))
            # store url
            if entry['url'] and entry['url_type']:
                url = entry['url']
                result_url = Url.query.filter_by(url=url).first()
                if result_url is None:
                    try:
                        db_url = Url(
                            url=url,
                            doi=doi,
                            url_type=entry['url_type']
                        )
                        db.session.add(db_url)
                        db.session.commit()
                        num_urls_added += 1
                    except:
                        print('ERROR: Can not import Url {0}.'.format(url))
        else:
            print('WARNING: DOI {} is not valid.'.format(entry['doi']))

    print('{0} doi\'s added to database.'.format(num_dois_added))
    print('{0} url\'s added to database.'.format(num_urls_added))

    return {'dois_added': dois_added, 'num_dois_added': num_dois_added, 'num_urls_added': num_urls_added}


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
        imp = Import('<API>', dumps(data))
        db.session.add(imp)
        db.session.commit()
        response = add_entries_to_database(data, imp.id)
        return response
    except:
        response = 'ERROR: Data import from API not working.'
        print(response)
        return response


def create_doi_new_urls(batch_size):
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    from app.models import Doi
    from app.models import Url
    import app

    num_urls_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    # get doi, url_doi_new=False and url
    result_join = db.session.query(Doi).join(Url).filter(Doi.doi == Url.doi).filter(Doi.url_doi_new == False).all()
    for i in range(0, len(result_join), batch_size):
        for d in result_join[i:i + batch_size]:
            doi_url_encoded = urlparse.quote(d.doi)
            url = 'https://doi.org/{0}'.format(doi_url_encoded)
            if url not in db_urls and url not in urls_added:
                try:
                    db_url = Url(
                        url=url,
                        doi=d.doi,
                        url_type='doi_new'
                    )
                    d.url_doi_new = True
                    db.session.add(db_url)
                    num_urls_added += 1
                    urls_added.append(url)
                except:
                    print('WARNING: Url {0} can not be created.'.format(url))
        db.session.commit()

    db.session.close()
    print('{0} new doi url\'s added to database.'.format(num_urls_added))


def create_doi_old_urls(batch_size):
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    from app.models import Doi
    from app.models import Url

    num_urls_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    # get doi, url_doi_old=False and url
    result_join = db.session.query(Doi).join(Url).filter(Doi.doi == Url.doi).filter(Doi.url_doi_old == False).all()
    for i in range(0, len(result_join), batch_size):
        for d in result_join[i:i+batch_size]:
            doi_url_encoded = urlparse.quote(d.doi)
            url = 'http://dx.doi.org/{0}'.format(doi_url_encoded)
            if url not in db_urls and url not in urls_added:
                try:
                    db_url = Url(
                        url=url,
                        doi=d.doi,
                        url_type='doi_old'
                    )
                    d.url_doi_old = True
                    db.session.add(db_url)
                    num_urls_added += 1
                    urls_added.append(url)
                except:
                    print('WARNING: Url {0} can not be created.'.format(url))
        db.session.commit()

    db.session.close()
    print('{0} old doi url\'s added to database.'.format(num_urls_added))


def create_doi_lp_urls():
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    from app.models import APIRequest
    from app.models import Doi
    from app.models import Url

    num_urls_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    # create doi landing page url
    result_join = db.session.query(Doi).join(Url).filter(Doi.doi == Url.doi).filter(Doi.url_doi_lp == False).all()
    for d in tqdm(result_join):
        doi_url_encoded = urlparse.quote(d.doi)
        url = 'https://doi.org/{0}'.format(doi_url_encoded)
        resp = request_doi_landingpage_api(url)
        resp_url = resp.url
        try:
            db_api = APIRequest(
                doi=d.doi,
                request_url=url,
                request_type='doi_landingpage',
                response_content=resp.content,
                response_status=resp.status_code
            )
            db.session.add(db_api)
        except:
            print('WARNING: APIRequest can not be created.')
        if resp_url not in db_urls and resp_url not in urls_added:
            db_url = Url(
                url=resp_url,
                doi=d.doi,
                url_type='doi_landingpage'
            )
            d.url_doi_lp = True
            db.session.add(db_url)
            num_urls_added += 1
            urls_added.append(resp_url)
        db.session.commit()

    db.session.close()
    print('{0} doi new landing page doi url\'s added to database.'.format(num_urls_added))


def request_doi_landingpage_api(url):
    return requests.get(url, allow_redirects=True)


def create_ncbi_urls(ncbi_tool, ncbi_email):
    """Create NCBI URL's from the identifier.

    https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/

    Parameters
    ----------
    ncbi_tool : string
        Name of tool, which want to connect to the NCBI API.
    email : string
        Email related to the app, used as credential for the request.

    """
    from app.models import APIRequest
    from app.models import Doi
    from app.models import Url

    num_urls_pm_added = 0
    num_urls_pmc_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    result_join = db.session.query(Doi).join(Url).filter(Doi.doi == Url.doi).filter(Doi.url_pm == False or Doi.url_pmc == False).all()
    for d in tqdm(result_join):
        # TODO: allows up to 200 ids sent at the same time
        # send request to NCBI API
        doi_url_encoded = urlparse.quote(d.doi)
        url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={0}'.format(doi_url_encoded)
        resp_data = request_ncbi_api(url, ncbi_tool, ncbi_email, d.doi)
        db_ncbi = APIRequest(
            # doi=d.doi,
            doi=d.doi,
            request_url=url,
            request_type='ncbi',
            response_content=dumps(resp_data),
            response_status=resp.status_code
        )
        db.session.add(db_ncbi)

        if 'records' in resp_data:
            # create PMC url
            if 'pmcid' in resp_data['records']:
                url_pmc = 'https://ncbi.nlm.nih.gov/pmc/articles/PMC{0}/'.format(
                    resp_data['records']['pmcid'])
                if url not in db_urls and url not in urls_added:
                    db_url_pmc = Url(
                        doi=d.doi,
                        url_type='pmc'
                    )
                    d.url_pmc = True
                    db.session.add(db_url_pmc)
                    num_urls_pmc_added += 1
                    urls_added.append(url_pmc)
            # create PM url
            if 'pmid' in resp_data['records']:
                url_pm = 'https://www.ncbi.nlm.nih.gov/pubmed/{0}'.format(
                    resp_data['records']['pmid'])
                if Url.query.filter_by(url=url_pm).first() is None:
                    db_url_pm = Url(
                        url=url_pm,
                        doi=d.doi,
                        url_type='pm'
                    )
                    d.url_pm = True
                    db.session.add(db_url_pm)
                    num_urls_pm_added += 1
                    urls_added.append(url_pmc)
        db.session.commit()

    db.session.close()
    print('{0} PM url\'s added to database.'.format(num_urls_pm_added))
    print('{0} PMC url\'s added to database.'.format(num_urls_pmc_added))


def request_ncbi_api(url, ncbi_tool, ncbi_email, doi):
    resp = requests.get(url, params={
        'tool': ncbi_tool,
        'email': ncbi_email,
        'idtype': 'doi',
        'versions': 'no',
        'format': 'json'
    })
    return resp.json()


def create_unpaywall_urls(email):
    """Create Unpaywall URL's from the identifier.

    https://unpaywall.org/products/api

    Parameters
    ----------
    email : string
        Email related to the app, used as credential for the request.

    """
    from app.models import APIRequest
    from app.models import Doi
    from app.models import Url

    num_urls_unpaywall_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    result_join = db.session.query(Doi).join(Url).filter(Doi.doi == Url.doi).filter(Doi.url_unpaywall == False).all()
    for d in tqdm(result_join):
        # send request to Unpaywall API
        url_dict = {}
        doi_url_encoded = urlparse.quote(d.doi)
        url = 'https://api.unpaywall.org/v2/{0}?email={1}'.format(doi_url_encoded, email)
        resp_data = request_unpaywall_api(url)
        db_api = APIRequest(
            doi=d.doi,
            request_url=url,
            request_type='unpaywall',
            response_content=dumps(resp_data),
            response_status=resp_data.status_code
        )
        d.url_unpaywall = True
        db.session.add(db_api)
        db.session.commit()

        # check if response includes needed data
        if 'doi_url' in resp_data:
            url_dict['unpaywall_doi_url'] = resp_data['doi_url']
        if 'oa_locations' in resp_data:
            for loc in resp_data['oa_locations']:
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
            if url not in db_urls and url not in urls_added:
                db_url = Url(
                    url=url,
                    doi=d.doi,
                    url_type=url_type
                )
                d.url_unpaywall = True
                db.session.add(db_url)
                num_urls_unpaywall_added += 1
                urls_added.append(url)
        db.session.commit()

    db.session.close()
    print('{0} Unpaywall url\'s added to database.'.format(num_urls_unpaywall_added))


def request_unpaywall_api(url):
    resp = requests.get(url)
    return resp.json()


def fb_requests(app_id, app_secret, batch_size):
    """Get app access token.

    Example Response:
    {'id': 'http://dx.doi.org/10.22230/src.2010v1n2a24',
    'engagement': { 'share_count': 0, 'comment_plugin_count': 0,
                    'reaction_count': 0, 'comment_count': 0}}
    """
    from app.models import FBRequest
    from app.models import Url

    payload = {'grant_type': 'client_credentials',
               'client_id': app_id,
               'client_secret': app_secret}
    try:
        response = requests.post(
            'https://graph.facebook.com/oauth/access_token?',
            params=payload)
    except requests.exceptions.RequestException:
        raise Exception()

    token = loads(response.text)
    fb_graph = GraphAPI(token['access_token'], version="2.10")

    fb_request_added = 0
    result_url = Url.query.all()

    for i in range(0, len(result_url), batch_size):
        batch = result_url[i:i + batch_size]
        url_list = []
        for row in batch:
            url_list.append(row.url)
        urls_response = fb_graph.get_objects(ids=url_list,
                                             fields="engagement,og_object")
        for key, value in urls_response.items():
            if urls_response:
                db_fb_request = FBRequest(
                    url=key,
                    response=value
                )
                db.session.add(db_fb_request)
                fb_request_added += 1
        db.session.commit()

    db.session.close()
    print('{0} Facebook openGraph request\'s added to database.'.format(fb_request_added))


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


def delete_apirequests():
    """Delete all api requests."""
    from app.models import APIRequest
    try:
        apirequests_deleted = db.session.query(APIRequest).delete()
        db.session.commit()
        print(apirequests_deleted, 'APIRequests\'s deleted from database.')
    except:
        db.session.rollback()
        print('ERROR: API requests\'s can not be deleted from database.')


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


def import_csv(table_names, delete_tables):
    """Import data coming from CSV file."""
    from app import import_csv_recreate
    from app import import_csv_append

    if delete_tables:
        import_csv_recreate(table_names)
    else:
        import_csv_append(table_names)


def import_csv_recreate(table_names):
    """Import data coming from CSV file.

    Delete all data in advance and do fresh import.

    """
    from app import delete_data
    from app.models import Import
    from app.models import Doi
    from app.models import Url
    from app.models import APIRequest
    from app.models import FBRequest

    table2model = {
        'doi': Doi,
        'url': Url,
        'api_request': APIRequest,
        'fb_request': FBRequest
    }

    delete_data()

    filename_list = [BASE_DIR + '/app/static/import/'+table+'.csv' for table in table_names]

    for idx, filename in enumerate(filename_list):
        model = table2model[table_names[idx]]
        df = pd.read_csv(filename)
        data_str = df.to_json(orient='records')
        db_imp = Import('<Import '+filename+'>', data_str)
        db.session.add(db_imp)
        db.session.commit()

        for row in df.to_dict(orient="records"):
            if table_names[idx] == 'doi':
                model = Doi(**row)
            elif table_names[idx] == 'url':
                model = Url(**row)
            elif table_names[idx] == 'api_request':
                model = APIRequest(**row)
            elif table_names[idx] == 'fb_request':
                model = FBRequest(**row)
            db.session.add(model)
        db.session.commit()


def import_csv_append(table_names):
    """Import data coming from CSV file.

    Insert all data in advance and do fresh import.

    """
    from app.models import Import
    from app.models import Doi
    from app.models import Url
    from app.models import APIRequest
    from app.models import FBRequest

    for table_name in table_names:
        filename = BASE_DIR + '/app/static/import/'+table_name+'.csv'
        df = pd.read_csv(filename, encoding='utf8')
        data_str = df.to_json(orient='records')
        data = df.to_dict(orient='records')
        db_imp = Import('<Import '+filename+'>', data_str)
        db.session.add(db_imp)
        db.session.commit()

        if table_name == 'doi':
            print('Import Doi table:')
            dois_added = 0
            for entry in tqdm(data):
                result_doi = Doi.query.filter_by(doi=entry['doi']).first()
                if result_doi is None:
                    if entry['is_valid'] == 't':
                        is_valid = True
                    elif entry['is_valid'] == 'f':
                        is_valid = False

                    if entry['url_doi_lp'] == 't':
                        url_doi_lp = True
                    elif entry['url_doi_lp'] == 'f':
                        url_doi_lp = False

                    if entry['url_doi_new'] == 't':
                        url_doi_new = True
                    elif entry['url_doi_new'] == 'f':
                        url_doi_new = False

                    if entry['url_doi_old'] == 't':
                        url_doi_old = True
                    elif entry['url_doi_old'] == 'f':
                        url_doi_old = False

                    if entry['url_pm'] == 't':
                        url_pm = True
                    elif entry['url_pm'] == 'f':
                        url_pm = False

                    if entry['url_pmc'] == 't':
                        url_pmc = True
                    elif entry['url_pmc'] == 'f':
                        url_pmc = False

                    if entry['url_unpaywall'] == 't':
                        url_unpaywall = True
                    elif entry['url_unpaywall'] == 'f':
                        url_unpaywall = False

                    db_doi = Doi(
                        doi=entry['doi'],
                        import_id=db_imp.id,
                        is_valid=is_valid,
                        pm_id=entry['pm_id'],
                        pmc_id=entry['pmc_id'],
                        date_published=datetime.strptime(entry['date_published'], '%Y-%m-%d %H:%M:%S'),
                        url_doi_lp=url_doi_lp,
                        url_doi_new=url_doi_new,
                        url_doi_old=url_doi_old,
                        url_pm=url_pm,
                        url_pmc=url_pmc,
                        url_unpaywall=url_unpaywall
                    )
                    db.session.add(db_doi)
                    db.session.commit()
                    dois_added += 1
            print('{0} doi\'s added to database.'.format(dois_added))
        elif table_name == 'url':
            print('Import Url table:')
            urls_added = 0
            for entry in tqdm(data):
                result_url = Url.query.filter_by(url=entry['url']).first()
                if result_url is None:
                    db_url = Url(
                        url=entry['url'],
                        doi=entry['doi'],
                        url_type=entry['url_type'],
                        date_added=datetime.strptime(entry['date_added'], '%Y-%m-%d %H:%M:%S.%f')
                    )
                    db.session.add(db_url)
                    db.session.commit()
                    urls_added += 1
            print('{0} url\'s added to database.'.format(urls_added))
        elif table_name == 'api_request':
            print('Import APIRequests table:')
            apirequests_added = 0
            for entry in tqdm(data):
                db_apirequest = APIRequest(
                    doi=entry['doi'],
                    request_url=entry['request_url'],
                    request_type=entry['request_type'],
                    response_content=entry['response_content'],
                    response_status=entry['response_status']
                )
                db.session.add(db_apirequest)
                db.session.commit()
                apirequests_added += 1
            print('{0} apirequest\'s added to database.'.format(apirequests_added))
        elif table_name == 'fb_request':
            print('Import FBRequests table:')
            fbrequests_added = 0
            for entry in tqdm(data):
                db_fbrequest = FBRequest(
                    url_url=entry['url_url'],
                    response=entry['response'],
                    reactions=entry['reactions'],
                    shares=entry['shares'],
                    comments=entry['comments'],
                    plugin_comments=entry['plugin_comments'],
                    timestamp=datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                )
                db.session.add(db_fbrequest)
                db.session.commit()
                fbrequests_added += 1
            print('{0} fbrequest\'s added to database.'.format(fbrequests_added))


def create_app():
    """Create application and load settings."""
    app = Flask(__name__)

    ENVIRONMENT = os.getenv('ENV', default='development')
    # TESTING = os.getenv('TESTING', default=False)
    print('* Updating App Mode to: ' + ENVIRONMENT)
    is_travis = os.getenv('TRAVIS', default=False)
    if not is_travis:
        print('* Loading User Settings.')
        app.config.from_pyfile(BASE_DIR+'/settings_user.py', silent=True)
    if ENVIRONMENT == 'development':
        print('* Loading Development Settings.')
        app.config.from_pyfile(BASE_DIR+'/settings_development.py', silent=True)
        app.config.from_object('settings_default.Development')
        if not is_travis:
            DebugToolbarExtension(app)
    elif ENVIRONMENT == 'production':
        print('* Loading Production Settings.')
        # order of settings loading: 1. settings file, 2. environment variable DATABASE_URL, 3. environment variable SQLALCHEMY_DATABASE_URI
        if not is_travis:
            app.config.from_pyfile(BASE_DIR+'/settings_production.py', silent=True)
        app.config.from_object('settings_default.Production')
    elif ENVIRONMENT == 'testing':
        print('* Loading Test Settings.')
        app.config['TESTING'] = True
        app.config.from_object('settings_default.Testing')
    if not is_travis:
        print('* Database: ' + app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)
    migrate.init_app(app, db)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # scheduler = BackgroundScheduler()
    # rate_limit = app.config['FB_HOURLY_RATELIMIT']
    # rate_intervall = 3600 / rate_limit
    # scheduler.add_job(, trigger='interval', seconds=rate_intervall)
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
