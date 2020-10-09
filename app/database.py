# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Database functions."""
# import app
# from app import db
from app.models import Doi, Import, Url, Request, FBRequest
from app.requests import request_doi_landingpage
from app.utils import is_valid_doi
from pandas import read_csv
from tqdm import tqdm
import os
from json import loads
from app import db
from datetime import datetime

try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


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

    num_dois_added = 0
    num_urls_added = 0
    dois_added = []
    url_import_lst = []
    url_list = []

    for entry in tqdm(data):
        dict_tmp = {}
        is_valid = validate_doi(entry["doi"])
        if is_valid:
            db_doi = None
            result_doi = Doi.query.filter_by(doi=entry["doi"]).first()
            if result_doi is None:
                try:
                    db_doi = Doi(
                        doi=entry["doi"],
                        date_published=datetime.strptime(entry["date"], "%Y-%m-%d"),
                        import_id=import_id,
                        is_valid=True,
                    )
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
        try:
            db_url = Url(url=d["url"], doi=d["doi"], url_type=d["url_type"])
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
                    try:
                        db_doi = Doi(
                            doi=doi,
                            date_published=datetime.strptime(entry["date"], "%Y-%m-%d"),
                            import_id=import_id,
                            is_valid=True,
                        )
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
                    try:
                        db_url = Url(url=url, doi=doi, url_type=entry["url_type"])
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
    try:
        imp = Import("<API>", dumps(data))
        db.session.add(imp)
        db.session.commit()
        response = add_entries_to_database(data, imp.id)
        return response
    except:
        response = "ERROR: Data import from API not working."
        print(response)
        return response


def add_import_entry(source, data):
    try:
        db_imp = Import(source, data)
        db.session.add(db_imp)
        db.session.commit()
        return db_imp
    except:
        print("ERROR: Import() can not be stored in Database.")
        return False


def validate_dois(data):
    lst_dois = []
    for idx, d in enumerate(data):
        lst_dois.append((d, is_valid_doi(d["doi"])))
    return lst_dois


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
    url_import_lst = []
    url_list = []

    filename = "{0}/{1}".format(BASE_DIR, filename)
    df = read_csv(filename, encoding="utf8")
    json_data_raw = df.to_json(orient="records")
    df = df.drop_duplicates(subset="doi")
    df = df.fillna(False)
    data = loads(df.to_json(orient="records"))

    db_imp = add_import_entry("<Init " + filename + ">", json_data_raw)

    data = validate_dois(data)

    for i in range(0, len(data), batch_size):
        for d, is_valid in tqdm(data[i : i + batch_size]):
            dict_tmp = {}
            if is_valid:
                if d["doi"] and d["date"]:
                    db_doi = None
                    try:
                        db_doi = Doi(
                            doi=d["doi"],
                            date_published=datetime.strptime(d["date"], "%Y-%m-%d"),
                            import_id=db_imp.id,
                            is_valid=True,
                        )
                        db.session.add(db_doi)
                        num_dois_added += 1
                        dois_added.append(d["doi"])
                    except:
                        print("ERROR: Can not import Doi {0}.".format(d["doi"]))

                if d["url"] and d["url_type"] and db_doi:
                    if d["url"] not in url_list:
                        try:
                            db_url = Url(
                                url=d["url"], doi=db_doi.doi, url_type=d["url_type"]
                            )
                            db.session.add(db_url)
                            num_urls_added += 1
                        except:
                            print("ERROR: Can not import Url {0}.".format(d["url"]))
                else:
                    print("WARNING: Entry {0} is not valid".format(d["doi"]))
            else:
                print("WARNING: DOI {} is not valid.".format(d["doi"]))
        db.session.commit()
    db.session.close()
    print("{0} doi's added to database.".format(num_dois_added))
    print("{0} url's added to database.".format(num_urls_added))

    return {
        "dois_added": dois_added,
        "num_dois_added": num_dois_added,
        "num_urls_added": num_urls_added,
    }


def create_doi_new_urls(batch_size):
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    # get doi, url_doi_new=False and url
    result_join = (
        db.session.query(Doi)
        .join(Url)
        .filter(Doi.doi == Url.doi)
        .filter(Doi.url_doi_new == False)
        .all()
    )
    for i in range(0, len(result_join), batch_size):
        for d in result_join[i : i + batch_size]:
            url = "https://doi.org/{0}".format(d.doi)
            if url not in db_urls and url not in urls_added:
                try:
                    db_url = Url(url=url, doi=d.doi, url_type="doi_new")
                    d.url_doi_new = True
                    db.session.add(db_url)
                    num_urls_added += 1
                    urls_added.append(url)
                except:
                    print("WARNING: Url {0} can not be created.".format(url))
        db.session.commit()

    db.session.close()
    print("{0} new doi url's added to database.".format(num_urls_added))


def create_doi_old_urls(batch_size):
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    # get doi, url_doi_old=False and url
    result_join = (
        db.session.query(Doi)
        .join(Url)
        .filter(Doi.doi == Url.doi)
        .filter(Doi.url_doi_old == False)
        .all()
    )
    for i in range(0, len(result_join), batch_size):
        for d in result_join[i : i + batch_size]:
            url = "http://dx.doi.org/{0}".format(quote(d.doi))
            if url not in db_urls and url not in urls_added:
                try:
                    db_url = Url(url=url, doi=d.doi, url_type="doi_old")
                    d.url_doi_old = True
                    db.session.add(db_url)
                    num_urls_added += 1
                    urls_added.append(url)
                except:
                    print("WARNING: Url {0} can not be created.".format(url))
        db.session.commit()

    db.session.close()
    print("{0} old doi url's added to database.".format(num_urls_added))


def create_doi_lp_urls():
    """Create URL's from the identifier.

    Creates the DOI URL's as part of the pre-processing.

    """
    num_urls_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    # create doi landing page url
    result_join = (
        db.session.query(Doi)
        .join(Url)
        .filter(Doi.doi == Url.doi)
        .filter(Doi.url_doi_lp == False)
        .all()
    )
    for d in tqdm(result_join):
        url = "https://doi.org/{0}".format(quote(d.doi))
        resp = request_doi_landingpage(url)
        resp_url = resp.url
        try:
            db_api = Request(
                doi=d.doi,
                request_url=url,
                request_type="doi_landingpage",
                response_content=resp.content,
                response_status=resp.status_code,
            )
            db.session.add(db_api)
        except:
            print("WARNING: Request can not be created.")
        if resp_url not in db_urls and resp_url not in urls_added:
            db_url = Url(url=resp_url, doi=d.doi, url_type="doi_landingpage")
            d.url_doi_lp = True
            db.session.add(db_url)
            num_urls_added += 1
            urls_added.append(resp_url)
        db.session.commit()

    db.session.close()
    print(
        "{0} doi new landing page doi url's added to database.".format(num_urls_added)
    )


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
    num_urls_pm_added = 0
    num_urls_pmc_added = 0
    db_urls = []
    urls_added = []

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    result_join = (
        db.session.query(Doi)
        .join(Url)
        .filter(Doi.doi == Url.doi)
        .filter(Doi.url_pm == False or Doi.url_pmc == False)
        .all()
    )
    for d in tqdm(result_join):
        # TODO: allows up to 200 ids sent at the same time
        # send request to NCBI API
        url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={0}".format(
            quote(d.doi)
        )
        resp_data = request_ncbi_api(url, ncbi_tool, ncbi_email, d.doi)
        db_ncbi = Request(
            # doi=d.doi,
            doi=d.doi,
            request_url=url,
            request_type="ncbi",
            response_content=dumps(resp_data),
            response_status=resp.status_code,
        )
        db.session.add(db_ncbi)

        if "records" in resp_data:
            # create PMC url
            if "pmcid" in resp_data["records"]:
                url_pmc = "https://ncbi.nlm.nih.gov/pmc/articles/PMC{0}/".format(
                    quote(resp_data["records"]["pmcid"])
                )
                if url not in db_urls and url not in urls_added:
                    db_url_pmc = Url(doi=d.doi, url_type="pmc")
                    d.url_pmc = True
                    db.session.add(db_url_pmc)
                    num_urls_pmc_added += 1
                    urls_added.append(url_pmc)
            # create PM url
            if "pmid" in resp_data["records"]:
                url_pm = "https://www.ncbi.nlm.nih.gov/pubmed/{0}".format(
                    resp_data["records"]["pmid"]
                )
                if Url.query.filter_by(url=url_pm).first() is None:
                    db_url_pm = Url(url=url_pm, doi=d.doi, url_type="pm")
                    d.url_pm = True
                    db.session.add(db_url_pm)
                    num_urls_pm_added += 1
                    urls_added.append(url_pmc)
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

    # get all URL's in the database
    query = db.session.query(Url.url)
    for row in query:
        db_urls.append(row.url)

    result_join = (
        db.session.query(Doi)
        .join(Url)
        .filter(Doi.doi == Url.doi)
        .filter(Doi.url_unpaywall == False)
        .all()
    )
    for d in tqdm(result_join):
        # send request to Unpaywall API
        url_dict = {}
        doi_url_encoded = urlparse.quote(d.doi)
        url = "https://api.unpaywall.org/v2/{0}?email={1}".format(
            doi_url_encoded, email
        )
        resp_data = request_unpaywall_api(url)
        db_api = Request(
            doi=d.doi,
            request_url=url,
            request_type="unpaywall",
            response_content=dumps(resp_data),
            response_status=resp_data.status_code,
        )
        d.url_unpaywall = True
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
                db_url = Url(url=url, doi=d.doi, url_type=url_type)
                d.url_unpaywall = True
                db.session.add(db_url)
                num_urls_unpaywall_added += 1
                urls_added.append(url)
        db.session.commit()

    db.session.close()
    print("{0} Unpaywall url's added to database.".format(num_urls_unpaywall_added))


def delete_dois():
    """Delete all doi entries."""
    try:
        dois_deleted = db.session.query(Doi).delete()
        db.session.commit()
        print(dois_deleted, "doi's deleted from database.")
    except:
        db.session.rollback()
        print("ERROR: Doi's can not be deleted from database.")


def delete_urls():
    """Delete all url entries."""
    try:
        urls_deleted = db.session.query(Url).delete()
        db.session.commit()
        print(urls_deleted, "url's deleted from database.")
    except:
        db.session.rollback()
        print("ERROR: Url's can not be deleted from database.")


def delete_requests():
    """Delete all api requests."""
    try:
        requests_deleted = db.session.query(Request).delete()
        db.session.commit()
        print(requests_deleted, "Requests's deleted from database.")
    except:
        db.session.rollback()
        print("ERROR: Requests's can not be deleted from database.")


def delete_fbrequests():
    """Delete all facebook requests."""
    try:
        fbrequests_deleted = db.session.query(FBRequest).delete()
        db.session.commit()
        print(fbrequests_deleted, "FBRequests's deleted from database.")
    except:
        db.session.rollback()
        print("ERROR: Facebook requests's can not be deleted from database.")


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
        BASE_DIR
        + "/app/static/export/"
        + datetime.today().strftime("%Y-%m-%d")
        + "_"
        + table
        + ".csv"
        for table in table_names
    ]

    for idx, filename in enumerate(filename_list):
        sql = "COPY " + table_names[idx] + " TO STDOUT DELIMITER ',' CSV HEADER;"
        cur.copy_expert(sql, open(filename, "w"))


def import_csv(table_names, delete_tables):
    """Import data coming from CSV file."""
    if delete_tables:
        import_csv_recreate(table_names)
    else:
        import_csv_append(table_names)


def import_csv_recreate(table_names):
    """Import data coming from CSV file.

    Delete all data in advance and do fresh import.

    """
    table2model = {
        "doi": Doi,
        "url": Url,
        "api_request": Request,
        "fb_request": FBRequest,
    }

    delete_data()

    filename_list = [
        BASE_DIR + "/app/static/import/" + table + ".csv" for table in table_names
    ]

    for idx, filename in enumerate(filename_list):
        model = table2model[table_names[idx]]
        df = pd.read_csv(filename)
        data_str = df.to_json(orient="records")
        db_imp = Import("<Import " + filename + ">", data_str)
        db.session.add(db_imp)
        db.session.commit()

        for row in df.to_dict(orient="records"):
            if table_names[idx] == "doi":
                model = Doi(**row)
            elif table_names[idx] == "url":
                model = Url(**row)
            elif table_names[idx] == "api_request":
                model = Request(**row)
            elif table_names[idx] == "fb_request":
                model = FBRequest(**row)
            db.session.add(model)
        db.session.commit()


def import_csv_append(table_names):
    """Import data coming from CSV file.

    Insert all data in advance and do fresh import.

    """

    for table_name in table_names:
        filename = BASE_DIR + "/app/static/import/" + table_name + ".csv"
        df = pd.read_csv(filename, encoding="utf8")
        data_str = df.to_json(orient="records")
        data = df.to_dict(orient="records")
        db_imp = Import("<Import " + filename + ">", data_str)
        db.session.add(db_imp)
        db.session.commit()

        if table_name == "doi":
            print("Import Doi table:")
            dois_added = 0
            for entry in tqdm(data):
                result_doi = Doi.query.filter_by(doi=entry["doi"]).first()
                if result_doi is None:
                    if entry["is_valid"] == "t":
                        is_valid = True
                    elif entry["is_valid"] == "f":
                        is_valid = False

                    if entry["url_doi_lp"] == "t":
                        url_doi_lp = True
                    elif entry["url_doi_lp"] == "f":
                        url_doi_lp = False

                    if entry["url_doi_new"] == "t":
                        url_doi_new = True
                    elif entry["url_doi_new"] == "f":
                        url_doi_new = False

                    if entry["url_doi_old"] == "t":
                        url_doi_old = True
                    elif entry["url_doi_old"] == "f":
                        url_doi_old = False

                    if entry["url_pm"] == "t":
                        url_pm = True
                    elif entry["url_pm"] == "f":
                        url_pm = False

                    if entry["url_pmc"] == "t":
                        url_pmc = True
                    elif entry["url_pmc"] == "f":
                        url_pmc = False

                    if entry["url_unpaywall"] == "t":
                        url_unpaywall = True
                    elif entry["url_unpaywall"] == "f":
                        url_unpaywall = False

                    db_doi = Doi(
                        doi=entry["doi"],
                        import_id=db_imp.id,
                        is_valid=is_valid,
                        pm_id=entry["pm_id"],
                        pmc_id=entry["pmc_id"],
                        date_published=datetime.strptime(
                            entry["date_published"], "%Y-%m-%d %H:%M:%S"
                        ),
                        url_doi_lp=url_doi_lp,
                        url_doi_new=url_doi_new,
                        url_doi_old=url_doi_old,
                        url_pm=url_pm,
                        url_pmc=url_pmc,
                        url_unpaywall=url_unpaywall,
                    )
                    db.session.add(db_doi)
                    db.session.commit()
                    dois_added += 1
            print("{0} doi's added to database.".format(dois_added))
        elif table_name == "url":
            print("Import Url table:")
            urls_added = 0
            for entry in tqdm(data):
                result_url = Url.query.filter_by(url=entry["url"]).first()
                if result_url is None:
                    db_url = Url(
                        url=entry["url"],
                        doi=entry["doi"],
                        url_type=entry["url_type"],
                        date_added=datetime.strptime(
                            entry["date_added"], "%Y-%m-%d %H:%M:%S.%f"
                        ),
                    )
                    db.session.add(db_url)
                    db.session.commit()
                    urls_added += 1
            print("{0} url's added to database.".format(urls_added))
        elif table_name == "api_request":
            print("Import Requests table:")
            requests_added = 0
            for entry in tqdm(data):
                db_request = Request(
                    doi=entry["doi"],
                    request_url=entry["request_url"],
                    request_type=entry["request_type"],
                    response_content=entry["response_content"],
                    response_status=entry["response_status"],
                )
                db.session.add(db_request)
                db.session.commit()
                requests_added += 1
            print("{0} request's added to database.".format(requests_added))
        elif table_name == "fb_request":
            print("Import FBRequests table:")
            fbrequests_added = 0
            for entry in tqdm(data):
                db_fbrequest = FBRequest(
                    url_url=entry["url_url"],
                    response=entry["response"],
                    reactions=entry["reactions"],
                    shares=entry["shares"],
                    comments=entry["comments"],
                    plugin_comments=entry["plugin_comments"],
                    timestamp=datetime.strptime(
                        entry["timestamp"], "%Y-%m-%d %H:%M:%S.%f"
                    ),
                )
                db.session.add(db_fbrequest)
                db.session.commit()
                fbrequests_added += 1
            print("{0} fbrequest's added to database.".format(fbrequests_added))
