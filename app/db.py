# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Database functions."""
import click
from datetime import datetime
from flask import current_app, Flask, g
from json import loads, dumps
import os
from pandas import read_csv
from psycopg2 import connect
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
from tqdm import tqdm

try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote

from app.config import get_config_name, get_config
from app.crud import create_entity, create_entities, get_all
from app.models import db, Doi, Import, Url, Request, FBRequest
from app.requests import (
    request_doi_landingpage,
    request_ncbi_api,
    request_unpaywall_api,
    get_GraphAPI,
    get_GraphAPI_urls,
    get_GraphAPI_token,
)
from app.utils import is_valid_doi


config_name = get_config_name()
config = get_config(config_name)


def get_db() -> Session:
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = db
    return g.db


def close_db(e=None) -> None:
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.session.close()


def init_db() -> None:
    """Conncet to database and create new tables."""
    db = get_db()
    db.create_all()


def drop_db() -> None:
    db = get_db()
    db.drop_all()


def dev():
    pass


def import_basedata(filename: str, reset: bool = False) -> None:
    """

    * preprocess data
        * read csv to pandas df (header: doi,url,url_type,date_published)
        * remove duplicates: doi, url
        * na mit None befüllen
        * validate doi
        * OPTIONAL: trim whitespace of doi, url, url_type and date_published fields => necessary? :OPTIONAL
    * create import entry and save id
    * if is_valid
        * create list of dicts for dois and list of dicts for urls
        * do bulk import of dois with batch_size
        * create all dois and save ids in list of url dicts
        * do bulk import of urls with batch_size
    """
    if reset:
        drop_db()
        init_db()

    num_dois_added = 0
    num_urls_added = 0
    dois_invalid = []

    db = get_db()
    batch_size = config.URL_BATCH_SIZE
    df = read_csv(filename, encoding="utf8")
    json_str = df.to_json(orient="records")
    df = df.drop_duplicates(subset="doi")
    df = df.drop_duplicates(subset="url")
    df = df.fillna(False)
    data = df.to_dict(orient="records")

    imp_dict = {
        "source": "<INIT " + filename + ">",
        "raw": json_str,
    }
    db_imp = create_entity(db, Import, imp_dict)
    import_id = db_imp.id

    doi_list = [doi.doi for doi in get_all(db, Doi)]
    url_list = [url.url for url in get_all(db, Url)]

    for i in range(0, len(data), batch_size):
        dois_added = []
        urls_added = []
        for d in tqdm(data[i : i + batch_size]):
            """
            d = {
                'url': 'http://www.cjc-online.ca/index.php/journal/article/view/1208',
                'doi': '10.22230/cjc.2001v26n1a1208',
                'url_type': 'ojs',
                'date_published': '2001-01-01'
            }
            """
            if is_valid_doi(d["doi"]):
                if d["doi"] not in doi_list:
                    if d["doi"] and d["date_published"]:
                        doi_dict = {
                            "doi": d["doi"],
                            "date_published": datetime.strptime(
                                d["date_published"], "%Y-%m-%d"
                            ),
                            "import_id": import_id,
                            "is_valid": True,
                        }
                        dois_added.append(doi_dict)
                if d["url"] not in url_list:
                    url_dict = {
                        "url": d["url"],
                        "doi": d["doi"],
                        "url_type": d["url_type"],
                    }
                    urls_added.append(url_dict)
            else:
                dois_invalid.append(d["doi"])
        create_entities(db, Doi, dois_added)
        num_dois_added += len(dois_added)
        create_entities(db, Url, urls_added)
        num_urls_added += len(urls_added)
    print("{0} doi's added to database.".format(num_dois_added))
    print("{0} url's added to database.".format(num_urls_added))
    return {
        "num_dois_added": num_dois_added,
        "num_urls_added": num_urls_added,
        "dois_invalid": dois_invalid,
    }


def create_doi_new_urls() -> None:
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    urls_added = []

    db = get_db()
    batch_size = config.URL_BATCH_SIZE

    url_list = [url.url for url in get_all(db, Url)]

    # get all DOIs, where url_doi_new=False
    list_dois = Doi.query.filter(Doi.url_doi_new == False).all()
    print("Found DOI's: {0}".format(len(list_dois)))

    for i in range(0, len(list_dois), batch_size):
        db_urls_added = []
        for row in tqdm(list_dois[i : i + batch_size]):
            url = "https://doi.org/{0}".format(row.doi)
            if url not in url_list and url not in urls_added:
                url_dict = {"url": url, "doi": row.doi, "url_type": "doi_new"}
                row.url_doi_new = True
                urls_added.append(url_dict["url"])
                db_urls_added.append(url_dict)
        create_entities(db, Url, db_urls_added)
        num_urls_added += len(db_urls_added)
    print('{0} "New DOI" URL\'s added to database.'.format(num_urls_added))


def create_doi_old_urls() -> None:
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    urls_added = []

    db = get_db()
    batch_size = config.URL_BATCH_SIZE

    url_list = [url.url for url in get_all(db, Url)]

    list_dois = Doi.query.filter(Doi.url_doi_old == False).all()
    print("Found DOI's: {0}".format(len(list_dois)))

    for i in range(0, len(list_dois), batch_size):
        db_urls_added = []
        for row in tqdm(list_dois[i : i + batch_size]):
            url = "http://dx.doi.org/{0}".format(quote(row.doi))
            if url not in url_list and url not in urls_added:
                url_dict = {"url": url, "doi": row.doi, "url_type": "doi_old"}
                row.url_doi_old = True
                urls_added.append(url_dict["url"])
                db_urls_added.append(url_dict)
        create_entities(db, Url, db_urls_added)
        num_urls_added += len(db_urls_added)
    print('{0} "Old DOI" URL\'s added to database.'.format(num_urls_added))


def create_doi_lp_urls() -> None:
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    num_requests_added = 0
    urls_added = []

    db = get_db()
    # batch_size = config.URL_BATCH_SIZE # TODO: identify default and best practice values
    batch_size = 20

    url_list = [url.url for url in get_all(db, Url)]

    list_dois = Doi.query.filter(Doi.url_doi_lp == False).all()
    print("Found DOI's: {0}".format(len(list_dois)))

    for i in range(0, len(list_dois), batch_size):
        db_urls_added = []
        db_requests_added = []
        for row in tqdm(list_dois[i : i + batch_size]):
            url = "https://doi.org/{0}".format(quote(row.doi))
            if url not in url_list + urls_added:
                resp = request_doi_landingpage(url)
                req_dict = {
                    "doi": row.doi,
                    "request_url": url,
                    "request_type": "doi_lp",
                    "response_content": resp.content,
                    "response_status": resp.status_code,
                }
                db_requests_added.append(req_dict)
                row.url_doi_lp = True
                if resp.url not in url_list + urls_added:
                    url_dict = {
                        "url": resp.url,
                        "doi": row.doi,
                        "url_type": "doi_lp",
                    }
                    db_urls_added.append(url_dict)
                    urls_added.append(url_dict["url"])
        create_entities(db, Request, db_requests_added)
        create_entities(db, Url, db_urls_added)
        num_urls_added += len(db_urls_added)
        num_requests_added += len(db_requests_added)
    print('{0} "Landing Page DOI" URL\'s added to database.'.format(num_urls_added))
    print("{0} Requests added to database.".format(num_requests_added))


def create_ncbi_urls() -> None:
    """Create NCBI URL's from the identifier.

    https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/

    API allows up to 200 ids sent at the same time.
    dois seperated with comma.

    """
    num_urls_pm_added = 0
    num_urls_pmc_added = 0
    num_requests_added = 0
    urls_added = []

    db = get_db()
    ncbi_tool = config.NCBI_TOOL
    ncbi_email = config.APP_EMAIL
    request_batch_size = 20
    doi_batch_size = 200

    url_list = [url.url for url in get_all(db, Url)]

    list_dois = Doi.query.filter(Doi.url_ncbi == False).all()
    print("Found DOI's: {0}".format(len(list_dois)))

    for i in range(0, len(list_dois), request_batch_size * doi_batch_size):
        db_urls_added = []
        db_requests_added = []
        if i + request_batch_size * doi_batch_size >= len(list_dois):
            end = len(list_dois)
        else:
            end = i + request_batch_size * doi_batch_size
        for j in tqdm(range(i, end, doi_batch_size)):
            if j + doi_batch_size >= len(list_dois):
                end = len(list_dois)
            else:
                end = j + doi_batch_size
            list_dois_tmp = list_dois[j:end]
            dois_requested = {}
            url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids="
            for row in list_dois_tmp:
                url += quote(row.doi) + ","
                dois_requested[row.doi] = row
            url = url[:-1]

            # send request to NCBI API
            resp = request_ncbi_api(url, ncbi_tool, ncbi_email)
            resp_data = resp.json()
            for doi, row in dois_requested.items():
                request_dict = {
                    "doi": doi,
                    "request_url": url,
                    "request_type": "ncbi",
                    "response_content": dumps(resp_data),
                    "response_status": resp.status_code,
                }
                db_requests_added.append(request_dict)
                row.url_ncbi = True

            if "records" in resp_data:
                for rec in resp_data["records"]:
                    # create PMC url
                    if "pmcid" in rec:
                        url_pmc = "https://ncbi.nlm.nih.gov/pmc/articles/PMC{0}/".format(
                            quote(rec["pmcid"])
                        )
                        if url_pmc not in url_list + urls_added:
                            url_dict = {
                                "url": url_pmc,
                                "doi": rec["doi"],
                                "url_type": "pmc",
                            }
                            db_urls_added.append(url_dict)
                            urls_added.append(url_pmc)
                            num_urls_pmc_added += 1
                            if rec["doi"] in dois_requested:
                                dois_requested[rec["doi"]].url_pmc = True
                    # create PM url
                    if "pmid" in rec:
                        url_pm = "https://www.ncbi.nlm.nih.gov/pubmed/{0}".format(
                            rec["pmid"]
                        )
                        if url_pm not in url_list + urls_added:
                            url_dict = {
                                "url": url_pm,
                                "doi": rec["doi"],
                                "url_type": "pm",
                            }
                            db_urls_added.append(url_dict)
                            urls_added.append(url_pm)
                            num_urls_pm_added += 1
                            if rec["doi"] in dois_requested:
                                dois_requested[rec["doi"]].url_pm = True
        create_entities(db, Request, db_requests_added)
        create_entities(db, Url, db_urls_added)
        num_requests_added += len(db_requests_added)
    print('{0} "PM" URL\'s added to database.'.format(num_urls_pm_added))
    print('{0} "PMC" URL\'s added to database.'.format(num_urls_pmc_added))
    print("{0} Requests added to database.".format(num_requests_added))


def create_unpaywall_urls() -> None:
    """Create Unpaywall URL's from the identifier.

    https://unpaywall.org/products/api

    """
    num_urls_unpaywall_added = 0
    num_requests_added = 0
    urls_added = []

    db = get_db()
    # batch_size = config.URL_BATCH_SIZE # TODO: identify default and best practice values
    email = config.APP_EMAIL
    batch_size = 20

    url_list = [url.url for url in get_all(db, Url)]

    list_dois = Doi.query.filter(Doi.url_unpaywall == False).all()
    print("Found DOI's: {0}".format(len(list_dois)))

    for i in range(0, len(list_dois), batch_size):
        db_urls_added = []
        db_requests_added = []
        for row in tqdm(list_dois[i : i + batch_size]):
            url_resp_dict = {}
            url = "https://api.unpaywall.org/v2/{0}?email={1}".format(
                quote(row.doi), email
            )
            resp = request_unpaywall_api(url)
            resp_data = resp.json()
            req_dict = {
                "doi": row.doi,
                "request_url": url,
                "request_type": "unpaywall",
                "response_content": dumps(resp_data),
                "response_status": resp.status_code,
            }
            db_requests_added.append(req_dict)
            row.url_unpaywall = True

            # check if response includes needed data
            if "doi_url" in resp_data:
                url_resp_dict["unpaywall:doi"] = resp_data["doi_url"]
            if "oa_locations" in resp_data:
                for loc in resp_data["oa_locations"]:
                    if "url_for_pdf" in loc:
                        if loc["url_for_pdf"]:
                            url_resp_dict["unpaywall:pdf"] = loc["url_for_pdf"]
                    if "url" in loc:
                        if loc["url"]:
                            url_resp_dict["unpaywall:url"] = loc["url"]
                    if "url_for_landing_page" in loc:
                        if loc["url_for_landing_page"]:
                            url_resp_dict["unpaywall:landing_page"] = loc[
                                "url_for_landing_page"
                            ]

            # store URL's in database
            for url_type, url in url_resp_dict.items():
                if url not in url_list + urls_added:
                    url_dict = {"url": url, "doi": row.doi, "url_type": url_type}
                    urls_added.append(url)
                    db_urls_added.append(url_dict)
        create_entities(db, Request, db_requests_added)
        create_entities(db, Url, db_urls_added)
        num_urls_unpaywall_added += len(db_urls_added)
        num_requests_added += len(db_requests_added)
    print('{0} "Unpaywall" URL\'s added to database.'.format(num_urls_unpaywall_added))
    print("{0} Requests added to database.".format(num_requests_added))
