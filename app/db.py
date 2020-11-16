# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Database functions."""
import click
from datetime import datetime
from flask import current_app, Flask, g
from flask.cli import with_appcontext
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
from app.models import Doi, Import, Url, Request, FBRequest
from app.requests import (
    request_doi_landingpage,
    request_ncbi_api,
    request_unpaywall_api,
    get_GraphAPI,
    get_GraphAPI_urls,
    get_GraphAPI_token,
)
from app.utils import is_valid_doi
from app.models import db, Table2Model


def get_db() -> Session:
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = db
    return g.db


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_db_command)
    app.cli.add_command(deploy_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(import_csv_command)
    app.cli.add_command(doi_new_command)
    app.cli.add_command(doi_old_command)
    app.cli.add_command(doi_lp_command)
    app.cli.add_command(ncbi_command)
    app.cli.add_command(unpaywall_command)
    app.cli.add_command(fb_command)
    app.cli.add_command(export_tables_command)


def close_db(e=None) -> None:
    """If this request connected to the database, close the
    connection.
    """
    g.pop("db", None)


def init_db(config_name: str = None) -> None:
    """Conncet to database and create new tables."""
    db = get_db()
    db.create_all()


def drop_db(config_name: str = None):
    db = get_db()
    db.drop_all()


def add_entries_to_database(data: list, import_id: str) -> dict:
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

    num_dois_added = 0
    num_urls_added = 0
    dois_added = []
    url_import_lst = []
    url_list = []
    db = get_db()

    for entry in tqdm(data):
        dict_tmp = {}
        is_valid = validate_doi(entry["doi"])
        if is_valid:
            db_doi = None
            result_doi = Doi.query.filter_by(doi=entry["doi"]).first()
            if result_doi is None:
                kwargs = {
                    "doi": entry["doi"],
                    "date_published": datetime.strptime(entry["date"], "%Y-%m-%d"),
                    "import_id": import_id,
                    "is_valid": True,
                }
                try:
                    db_doi = Doi(**kwargs)
                    db.session.add(db_doi)
                    num_dois_added += 1
                    dois_added.append(entry["doi"])
                    db.session.commit()
                except:
                    print("ERROR: Can not import Doi {0}.".format(entry["doi"]))
                if entry["url"] and entry["url_type"] and db_doi:
                    if entry["url"] not in url_list:
                        url_list.append(entry["url"])
                        dict_tmp["doi"] = db_doi.doi
                        dict_tmp["url"] = entry["url"]
                        dict_tmp["url_type"] = entry["url_type"]
                        url_import_lst.append(dict_tmp)
            else:
                print("WARNING: Entry {0} is not valid".format(entry["doi"]))
        else:
            print("WARNING: DOI {} is not valid.".format(entry["doi"]))
    db.session.commit()

    for d in url_import_lst:
        kwargs = {"url": d["url"], "doi": d["doi"], "url_type": d["url_type"]}
        try:
            db_url = Url(**kwargs)
            db.session.add(db_url)
            num_urls_added += 1
        except:
            print("ERROR: Can not import Url {0}.".format(d["url"]))
    db.session.commit()
    db.session.close()
    print("{0} doi's added to database.".format(num_dois_added))
    print("{0} url's added to database.".format(num_urls_added))

    return {
        "dois_added": dois_added,
        "num_dois_added": num_dois_added,
        "num_urls_added": num_urls_added,
    }

    for entry in tqdm(data):
        is_valid = validate_doi(entry["doi"])
        # TODO: what if not valid? user does not get it back in the api response.
        if is_valid:
            if entry["doi"] and entry["date"]:
                doi = entry["doi"]
                result_doi = Doi.query.filter_by(doi=doi).first()
                if result_doi is None:
                    kwargs = {
                        "doi": doi,
                        "date_published": datetime.strptime(entry["date"], "%Y-%m-%d"),
                        "import_id": import_id,
                        "is_valid": True,
                    }
                    try:
                        db_doi = Doi(**kwargs)
                        db.session.add(db_doi)
                        db.session.commit()
                        num_dois_added += 1
                        dois_added.append(doi)
                    except:
                        print("ERROR: Can not import Doi {0}.".format(doi))
                else:
                    doi = result_doi.doi
            else:
                print("WARNING: Entry {0} is not valid".format(doi))
            # store url
            if entry["url"] and entry["url_type"]:
                url = entry["url"]
                result_url = Url.query.filter_by(url=url).first()
                if result_url is None:
                    kwargs = {"url": url, "doi": doi, "url_type": entry["url_type"]}
                    try:
                        db_url = Url(**kwargs)
                        db.session.add(db_url)
                        db.session.commit()
                        num_urls_added += 1
                    except:
                        print("ERROR: Can not import Url {0}.".format(url))
        else:
            print("WARNING: DOI {} is not valid.".format(entry["doi"]))

    print("{0} doi's added to database.".format(num_dois_added))
    print("{0} url's added to database.".format(num_urls_added))

    return {
        "dois_added": dois_added,
        "num_dois_added": num_dois_added,
        "num_urls_added": num_urls_added,
    }


def import_dois_from_api(data: dict) -> Query:
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
    db = get_db()
    try:
        imp = Import(
            "<API " + datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + ">", dumps(data)
        )
        db.session.add(imp)
        db.session.commit()
        response = add_entries_to_database(data, imp.id)
        return response
    except:
        response = "ERROR: Data import from API not working."
        print(response)
        return response


def import_init_csv(filename, batch_size):
    """Import DOI's from a csv file.

    Imports the DOI's from a csv file into the database. Stores the raw data
    and adds dois in table. The data must contain an
    attribute `doi`, and optionally `url`, `url_type` and `date`.
    For test purposes, there is a file with 100 entries you can use.
    Checks, if duplicate dois are in the file and removes them.

    Parameters
    ----------
    filename : string
        Relative filepath for the csv file, relative from the root dir.

    Returns
    -------
    bool
        True, if import worked, False if not.

    """
    num_dois_added = 0
    num_urls_added = 0
    dois_added = []
    urls_added = []
    lst_invalid_dois = []

    db = get_db()
    filename = "{0}/{1}".format(filename)
    df = read_csv(filename, encoding="utf8")
    json_str = df.to_json(orient="records")
    df = df.drop_duplicates(subset="doi")
    df = df.drop_duplicates(subset="url")
    df = df.fillna(False)
    data = df.to_dict(orient="records")

    try:
        db_imp = Import("<INIT " + filename + ">", json_str)
        db.session.add(db_imp)
        db.session.commit()
    except:
        print("ERROR: Import() can not be stored in Database.")

    query_dois = db.session.query(Doi.doi)
    doi_list = [row[0] for row in query_dois]

    query_urls = db.session.query(Url.url)
    url_list = [row[0] for row in query_urls]

    for i in range(0, len(data), batch_size):
        dois_added_tmp = []
        urls_added_tmp = []
        for d in tqdm(data[i : i + batch_size]):
            """
            d = {
                'url': 'http://www.cjc-online.ca/index.php/journal/article/view/1208',
                'doi': '10.22230/cjc.2001v26n1a1208',
                'url_type': 'ojs',
                'date': '2001-01-01'
            }
            """
            if d["doi"] not in doi_list:
                if is_valid_doi(d["doi"]):
                    db_doi = None
                    if d["doi"] and d["date"]:
                        kwargs = {
                            "doi": d["doi"],
                            "date_published": datetime.strptime(d["date"], "%Y-%m-%d"),
                            "import_id": db_imp.id,
                            "is_valid": True,
                        }
                        # print(kwargs)
                        try:
                            db_doi = Doi(**kwargs)
                            db.session.add(db_doi)
                            num_dois_added += 1
                            dois_added_tmp.append(d["doi"])
                        except:
                            print('ERROR: Can not import DOI "{0}"'.format(d["doi"]))
            else:
                lst_invalid_dois.append(d["doi"])
        db.session.commit()
        dois_added = dois_added + dois_added_tmp
        doi_list = doi_list + dois_added_tmp

        for d in tqdm(data[i : i + batch_size]):
            if d["doi"] in dois_added_tmp:
                if d["url"] not in url_list:
                    if d["url"] and d["url_type"]:
                        kwargs = {
                            "url": d["url"],
                            "doi": d["doi"],
                            "url_type": d["url_type"],
                        }
                        # print(kwargs)
                        try:
                            db_url = Url(**kwargs)
                            db.session.add(db_url)
                            num_urls_added += 1
                            urls_added_tmp.append(d["url"])
                        except:
                            print('ERROR: Can not import Url "{0}"'.format(d["url"]))
        db.session.commit()
        urls_added = urls_added + urls_added_tmp
        url_list = url_list + urls_added_tmp
    db.session.close()
    print("{0} doi's added to database.".format(num_dois_added))
    print("{0} url's added to database.".format(num_urls_added))

    return {
        "dois_added": dois_added,
        "invalid_dois": lst_invalid_dois,
        "num_dois_added": num_dois_added,
        "num_urls_added": num_urls_added,
    }


def create_doi_new_urls(batch_size):
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    urls_added = []
    db = get_db()
    config_name = get_config_name()
    config = get_config(config_name)
    batch_size = config.URL_BATCH_SIZE

    query_urls = db.query(Url.url)
    url_list = [row[0] for row in query_urls]

    # get all DOIs, where url_doi_new=False
    query_result = db.query(Doi).filter(Doi.url_doi_new == False).all()
    print("Found DOI's to be processed: {0}".format(len(query_result)))

    for i in range(0, len(query_result), batch_size):
        for row in tqdm(query_result[i : i + batch_size]):
            url = "https://doi.org/{0}".format(row.doi)
            if url not in url_list and url not in urls_added:
                kwargs = {"url": url, "doi": row.doi, "url_type": "doi_new"}
                try:
                    db_url = Url(**kwargs)
                    row.url_doi_new = True
                    db.add(db_url)
                    num_urls_added += 1
                    urls_added.append(url)
                except:
                    print("WARNING: Url {0} can not be created.".format(url))
        db.commit()
    db.close()
    print("{0} new doi url's added to database.".format(num_urls_added))


def create_doi_old_urls(batch_size):
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    urls_added = []

    db = get_db()

    query_urls = db.session.query(Url.url)
    url_list = [row[0] for row in query_urls]

    # get all DOIs, where url_doi_old=False
    query_result = db.session.query(Doi).filter(Doi.url_doi_old == False).all()
    print("Found DOI's to be processed: {0}".format(len(query_result)))

    for i in range(0, len(query_result), batch_size):
        for d in tqdm(query_result[i : i + batch_size]):
            url = "http://dx.doi.org/{0}".format(quote(d.doi))
            if url not in url_list and url not in urls_added:
                kwargs = {"url": url, "doi": d.doi, "url_type": "doi_old"}
                try:
                    db_url = Url(**kwargs)
                    d.url_doi_old = True
                    db.add(db_url)
                    num_urls_added += 1
                    urls_added.append(url)
                except:
                    print("WARNING: Url {0} can not be created.".format(url))
        db.commit()
    db.close()
    print("{0} old doi url's added to database.".format(num_urls_added))


def create_doi_lp_urls():
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    db_urls = []
    urls_added = []
    db = get_db()

    query_urls = db.session.query(Url.url)
    url_list = [row[0] for row in query_urls]

    # get all DOIs, where url_doi_lp=False
    query_result = db.session.query(Doi).filter(Doi.url_doi_lp == False).all()
    print("Found DOI's to be processed: {0}".format(len(query_result)))

    batch_size = 100
    for i in range(0, len(query_result), batch_size):
        for row in tqdm(query_result[i : i + batch_size]):
            # create doi landing page url
            url = "https://doi.org/{0}".format(quote(row.doi))
            if url not in url_list:
                if url not in urls_added:
                    resp = request_doi_landingpage(url)
                    resp_url = resp.url
                    kwargs = {
                        "doi": row.doi,
                        "request_url": url,
                        "request_type": "doi_landingpage",
                        "response_content": resp.content,
                        "response_status": resp.status_code,
                    }
                    try:
                        db_api = Request(**kwargs)
                        db.session.add(db_api)
                    except:
                        print("ERROR: Request can not be created.")
                    if resp_url not in url_list + urls_added:
                        kwargs = {
                            "url": resp_url,
                            "doi": row.doi,
                            "url_type": "doi_landingpage",
                        }
                        try:
                            db_url = Url(**kwargs)
                            row.url_doi_lp = True
                            db.session.add(db_url)
                            num_urls_added += 1
                            urls_added.append(resp_url)
                        except:
                            print(
                                'ERROR: Url "{0}" can not be created.'.format(resp_url)
                            )
            else:
                row.url_doi_lp = True
        db.session.commit()
    db.session.close()
    print(
        "{0} doi new landing page doi url's added to database.".format(num_urls_added)
    )


def create_ncbi_urls(ncbi_tool, ncbi_email):
    """Create NCBI URL's from the identifier.

    https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/

    API allows up to 200 ids sent at the same time.
    dois seperated with comma.

    Parameters
    ----------
    ncbi_tool : string
        Name of tool, which want to connect to the NCBI API.
    email : string
        Email related to the app, used as credential for the request.

    """
    num_urls_pm_added = 0
    num_urls_pmc_added = 0
    urls_added = []
    db = get_db()

    query_urls = db.session.query(Url.url)
    url_list = [row[0] for row in query_urls]

    # get all DOIs, where url_doi_ncbi=False
    query_result = db.session.query(Doi).filter(Doi.url_ncbi == False).all()

    # url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids="
    # # doi1 = "10.22230/cjc.2001v26n1a1208"
    # # doi2 = "10.22230/cjc.2013v38n1a2578"
    # doi1 = "10.1371/journal.pone.0149989"
    # doi2 = "10.1371/journal.pone.0141854"
    # url = url + quote(doi1) + "," + quote(doi2)
    # resp = request_ncbi_api(url, ncbi_tool, ncbi_email)
    # resp_data = resp.json()
    # print(resp_data)

    batch_size = 200
    for i in range(0, len(query_result), batch_size):
        url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids="
        dois_requested = {}
        for row in tqdm(query_result[i : i + batch_size]):
            url += quote(row.doi) + ","
            dois_requested[row.doi] = row

        # send request to NCBI API
        url = url[:-1]
        resp = request_ncbi_api(url, ncbi_tool, ncbi_email)
        resp_data = resp.json()
        for doi, row in dois_requested.items():
            kwargs = {
                "doi": doi,
                "request_url": url[:512],
                "request_type": "ncbi",
                "response_content": dumps(resp_data),
                "response_status": resp.status_code,
            }
            try:
                db_ncbi = Request(**kwargs)
                db.session.add(db_ncbi)
                row.url_ncbi = True
            except:
                print("WARNING: Can not store Request.")

        if "records" in resp_data:
            for rec in resp_data["records"]:
                # create PMC url
                if "pmcid" in rec:
                    url_pmc = "https://ncbi.nlm.nih.gov/pmc/articles/PMC{0}/".format(
                        quote(rec["pmcid"])
                    )
                    if url_pmc not in url_list and url_pmc not in urls_added:
                        kwargs = {"url": url_pmc, "doi": rec["doi"], "url_type": "pmc"}
                        db_url_pmc = Url(**kwargs)
                        db.session.add(db_url_pmc)
                        num_urls_pmc_added += 1
                        urls_added.append(url_pmc)
                        if rec["doi"] in dois_requested:
                            dois_requested[rec["doi"]].url_pmc = True
                # create PM url
                if "pmid" in rec:
                    url_pm = "https://www.ncbi.nlm.nih.gov/pubmed/{0}".format(
                        rec["pmid"]
                    )
                    if url_pm not in url_list and url_pm not in urls_added:
                        kwargs = {"url": url_pm, "doi": rec["doi"], "url_type": "pm"}
                        db_url_pm = Url(**kwargs)
                        db.session.add(db_url_pm)
                        num_urls_pm_added += 1
                        urls_added.append(url_pm)
                        if rec["doi"] in dois_requested:
                            dois_requested[rec["doi"]].url_pm = True

        db.session.commit()
    db.session.close()
    print("{0} PM url's added to database.".format(num_urls_pm_added))
    print("{0} PMC url's added to database.".format(num_urls_pmc_added))


def create_unpaywall_urls(email):
    """Create Unpaywall URL's from the identifier.

    https://unpaywall.org/products/api

    Parameters
    ----------
    email : string
        Email related to the app, used as credential for the request.

    """
    num_urls_unpaywall_added = 0
    db_urls = []
    urls_added = []
    db = get_db()

    query_urls = db.session.query(Url.url)
    db_urls = [row[0] for row in query_urls]

    # get all DOIs, where url_doi_ncbi=False
    query_doi = db.session.query(Doi).filter(Doi.url_unpaywall == False).all()
    for row in tqdm(query_doi):
        # send request to Unpaywall API
        url_dict = {}
        url = "https://api.unpaywall.org/v2/{0}?email={1}".format(quote(row.doi), email)
        resp = request_unpaywall_api(url)
        resp_data = resp.json()
        kwargs = {
            "doi": row.doi,
            "request_url": url,
            "request_type": "unpaywall",
            "response_content": dumps(resp_data),
            "response_status": resp.status_code,
        }
        db_api = Request(**kwargs)
        row.url_unpaywall = True
        db.session.add(db_api)
        db.session.commit()

        # check if response includes needed data
        if "doi_url" in resp_data:
            url_dict["unpaywall_doi_url"] = resp_data["doi_url"]
        if "oa_locations" in resp_data:
            for loc in resp_data["oa_locations"]:
                if "url_for_pdf" in loc:
                    if loc["url_for_pdf"]:
                        url_dict["unpaywall_url_for_pdf"] = loc["url_for_pdf"]
                if "url" in loc:
                    if loc["url"]:
                        url_dict["unpaywall_url"] = loc["url"]
                if "url_for_landing_page" in loc:
                    if loc["url_for_landing_page"]:
                        url_dict["unpaywall_url_for_landing_page"] = loc[
                            "url_for_landing_page"
                        ]

        # store URL's in database
        for url_type, url in url_dict.items():
            if url not in db_urls and url not in urls_added:
                kwargs = {"url": url, "doi": row.doi, "url_type": url_type}
                db_url = Url(**kwargs)
                db.session.add(db_url)
                num_urls_unpaywall_added += 1
                urls_added.append(url)
        db.session.commit()

    db.session.close()
    print("{0} Unpaywall url's added to database.".format(num_urls_unpaywall_added))


def get_fb_data(app_id, app_secret, batch_size):
    """Get app access token.

    Example Response:
    {'id': 'http://dx.doi.org/10.22230/src.2010v1n2a24', 'engagement': { 'share_count': 0, 'comment_plugin_count': 0, 'reaction_count': 0, 'comment_count': 0}}
    """
    db = get_db()
    token = get_GraphAPI_token(app_id, app_secret)
    fb_graph = get_GraphAPI(token["access_token"], version="3.1")

    fb_request_added = 0
    result_url = Url.query.all()

    for i in range(0, len(result_url), batch_size):
        batch = result_url[i : i + batch_size]
        single_request_url_list = [row.url for row in batch]

        urls_response = get_GraphAPI_urls(fb_graph, single_request_url_list)
        for url, response in urls_response.items():
            kwargs = {
                "url_url": url,
                "response": dumps(response),
                "reactions": response["engagement"]["reaction_count"],
                "shares": response["engagement"]["share_count"],
                "comments": response["engagement"]["comment_count"],
                "plugin_comments": response["engagement"]["comment_plugin_count"],
                "timestamp": datetime.now(),
            }
            db_fb_request = FBRequest(**kwargs)
            db.session.add(db_fb_request)
            fb_request_added += 1
        db.session.commit()

    db.session.close()
    print(
        "{0} Facebook openGraph request's added to database.".format(fb_request_added)
    )


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
    filename_list = [
        "data/export/"
        + datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
        + "_"
        + table
        + ".csv"
        for table in table_names
    ]

    for idx, filename in enumerate(filename_list):
        sql = (
            "COPY "
            + table_names[idx]
            + " TO STDOUT (FORMAT CSV, DELIMITER ',', HEADER true);"
        )
        cur.copy_expert(sql, open(filename, "w"))


def import_csv_reset(table_names, prefix):
    """Import data coming from CSV file.

    Delete all data in advance and do fresh import.

    """
    table2model = {
        "imports": Import,
        "dois": Doi,
        "urls": Url,
        "requests": Request,
        "fbrequests": FBRequest,
    }

    db = get_db()
    db.drop_all()
    db.create_all()
    sleep(5)
    #
    filename_list = ["data/import/" + prefix + table + ".csv" for table in table_names]

    for idx, filename in enumerate(filename_list):
        model = table2model[table_names[idx]]
        df = read_csv(filename, true_values=["t", "true"], false_values=["f", "false"])

        for d in df.to_dict(orient="records"):
            if table_names[idx] == "imports":
                table = Import(**d)
            elif table_names[idx] == "dois":
                table = Doi(**d)
            elif table_names[idx] == "urls":
                table = Url(**d)
            elif table_names[idx] == "requests":
                table = Request(**d)
            elif table_names[idx] == "fbrequests":
                table = FBRequest(**d)
            db.session.add(table)
        db.session.commit()


def import_csv_append(table_names, prefix):
    """Import data coming from CSV file.

    Insert all data in advance and do fresh import.

    """
    db = get_db()
    for table_name in table_names:
        filename = "data/import/" + prefix + table_name + ".csv"
        df = read_csv(
            filename,
            encoding="utf8",
            true_values=["t", "true"],
            false_values=["f", "false"],
        )
        data = df.to_dict(orient="records")

        if table_name == "imports":
            print("Import Import table:")
            imports_added = 0
            try:
                db_imp = Import(
                    "<IMPORT_APPEND " + filename + ">", df.to_json(orient="records")
                )
                db.session.add(db_imp)
                db.session.commit()
            except:
                print("ERROR: Import() can not be stored in Database.")
        elif table_name == "dois":
            print("Import Doi table:")
            dois_added = 0
            query_dois = db.session.query(Doi.doi)
            db_dois = [row[0] for row in query_dois]
            for d in tqdm(data):
                if d["doi"] not in db_dois:
                    db_doi = Doi(**d)
                    db.session.add(db_doi)
                    dois_added += 1
            db.session.commit()
            print("{0} DOI's added to database.".format(dois_added))
        elif table_name == "urls":
            print("Import Url table:")
            urls_added = 0
            query_urls = db.session.query(Url.url)
            db_urls = [row[0] for row in query_urls]
            for d in tqdm(data):
                if d["url"] not in db_urls:
                    db_url = Url(**d)
                    db.session.add(db_url)
                    urls_added += 1
            db.session.commit()
            print("{0} URL's added to database.".format(urls_added))
        elif table_name == "requests":
            print("Import Requests table:")
            requests_added = 0
            for d in tqdm(data):
                del d["id"]
                db_request = Request(**d)
                db.session.add(db_request)
                requests_added += 1
            db.session.commit()
            print("{0} Requests added to database.".format(requests_added))
        elif table_name == "fbrequests":
            print("Import FBRequests table:")
            fbrequests_added = 0
            for d in tqdm(data):
                del d["id"]
                db_fbrequest = FBRequest(**d)
                db.session.add(db_fbrequest)
                fbrequests_added += 1
            db.session.commit()
            print("{0} FBRequests added to database.".format(fbrequests_added))


@click.command("initdb")
@with_appcontext
def init_db_command() -> None:
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("dropdb")
@with_appcontext
def drop_db_command() -> None:
    """Clear existing data and create new tables."""
    drop_db()
    click.echo("Dropped all tables in the database.")


@click.command("deploy")
@with_appcontext
def deploy_command() -> None:
    """Run deployment tasks."""
    click.echo("App deployed.")


@click.command("resetdb")
@with_appcontext
def reset_db_command() -> None:
    """Delete all entries in all tables."""
    drop_db()
    init_db()
    click.echo("Dataset reseted")


@click.command("doi-new")
def doi_new_command() -> None:
    """Create the new doi URL's."""
    create_doi_new_urls()


@click.command("doi-old")
def doi_old_command() -> None:
    """Create the old doi URL's."""
    create_doi_old_urls(current_app.config["URL_BATCH_SIZE"])


@click.command("doi-lp")
def doi_lp_command() -> None:
    """Create the doi landing page URL's."""
    create_doi_lp_urls()


@click.command("ncbi")
def ncbi_command() -> None:
    """Create the NCBI URL's."""
    create_ncbi_urls(current_app.config["NCBI_TOOL"], current_app.config["APP_EMAIL"])


@click.command("unpaywall")
def unpaywall_command() -> None:
    """Create the Unpaywall URL's."""
    create_unpaywall_urls(current_app.config["APP_EMAIL"])


@click.command("fb")
def fb_command() -> None:
    """Create the Facebook request."""
    get_fb_data(
        current_app.config["FB_APP_ID"],
        current_app.config["FB_APP_SECRET"],
        current_app.config["FB_BATCH_SIZE"],
    )


# @click.command("import-csv")
# def import_csv_command(filename: str = None):
#     """Import raw data from csv file.

#     The filepath can be manually passed with the argument `filename`.

#     Parameters
#     ----------
#     filename : string
#         Relative filepath to the csv file. Defaults to None, if not passed as an
#         argument via the command line. Relative to root.

#     """
#     if filename is None:
#         if "CSV_FILENAME" in current_app.config:
#             filename = current_app.config["CSV_FILENAME"]
#         else:
#             print("No CSV filename.")
#     batch_size = current_app.config["URL_BATCH_SIZE"]
#     import_init_csv(filename, batch_size)


@click.command("export-tables")
def export_tables_command(table_names: str = None):
    """Export tables passed as string, seperated by comma.

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    if not table_names:
        table_names = "imports,dois,urls,requests,fbrequests"

    table_names = table_names.split(",")
    export_tables_to_csv(table_names, current_app.config["SQLALCHEMY_DATABASE_URI"])


@click.command("import-csv")
def import_csv_command(
    table_names: str = None, import_type: str = "append", prefix: str = ""
):
    """Import data.

    table_names must be passed in the right order.
    e.g. 'doi,url,api_request,fb_request'

    Files must be available as:
        fb_request.csv, api_request.csv, doi.csv, url.csv

    Import_type: append or reset

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    if not table_names or table_names == "":
        table_names = ["imports", "dois", "urls", "requests", "fbrequests"]
    else:
        table_names = [table_name.strip() for table_name in table_names.split(",")]
    if import_type == "reset":
        import_csv_reset(table_names, prefix)
    elif import_type == "append" or import_type == False or import_type is None:
        import_csv_append(table_names, prefix)