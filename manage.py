import pandas as pd
import numpy as np
import re
import datetime
import time
import sys
import json
import requests
from dateutil.parser import parse
from random import shuffle
from pathlib import Path
import lxml.etree as ET
from flask_script import Manager, Server, Command, prompt_bool
from flask_script.commands import ShowUrls, Clean
from app import create_app
from app.models import db, Publication


app = create_app()
manager = Manager(app)


class CreateDb(Command):
    """ Creates a database with all of the tables defined in
        your SQLAlchemy models
    """

    def run(self):
        db.create_all()


# class DropDb(Command):
#     """ Drop all tables from database.
#     """
#
#     def run(self):
#         if prompt_bool('Are you sure you want to lose all your data'):
#             db.drop_all()
#
#
# class RecreateDb(Command):
#     "Recreates database tables (same as issuing 'drop' and then 'create')"
#
#     def run(self):
#         DropDb.run()
#         CreateDb.run()
#
#
# class PopulateDb(Command):
#     "Populate database with default data"
#     from fixtures import dbfixture
#
#     def run(self):
#         if default_data:
#             from fixtures.default_data import all
#             default_data = dbfixture.data(*all)
#             default_data.setup()
#
#         if sample_data:
#             from fixtures.sample_data import all
#             sample_data = dbfixture.data(*all)
#             sample_data.setup()


class ImportCsv(Command):
    """ Imports the data.

    """

    # def validate_doi(self, doi):
    #     """
    #
    #
    #         https://www.crossref.org/blog/dois-and-matching-regular-expressions/
    #     """
    #     return False

    def run(self):
        df_testsize = 5

        # import csv to pandas dataframe
        df = pd.read_csv('app/static/data/PKP_20171220_100.csv', encoding='utf8', parse_dates=True)
        df = df.drop_duplicates()

        # validate dois
        patterns = [
            r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$",
            r"^10.1002/[^\s]+$",
            r"^10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d$",
            r"^10.1021/\w\w\d+$",
            r"^10.1207\/[\w\d]+\&\d+_\d+$"
        ]
        valid_dois = []
        for doi in df['doi']:
            if type(doi) != str:
                valid_dois.append(False)
            else:
                for pat in patterns:
                    if re.match(pat, doi, re.IGNORECASE):
                        valid_dois.append(True)
        df = df[valid_dois]
        df = df.drop_duplicates().set_index('doi')
        df = df[:df_testsize]

        # request data from ncbi
        url_base = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0'
        batchsize = 200
        df['pmid'] = None
        df['pmc'] = None
        df['ncbi_ts'] = None
        df['ncbi_errmsg'] = None
        params = {
            'email': 'aenkhbay@sfu.ca',
            'tool': 'ScholCommLab ID Crawler - scholcommlab.ca',
            'idtype': 'doi',
            'versions': 'no',
            'format': 'json'
        }
        dois = list(set(df.index.tolist()))
        batches = range(0, len(dois), batchsize)
        for batch_start in batches:
            now = datetime.datetime.now()
            batch = dois[batch_start:batch_start + batchsize]  # the result might be shorter than batchsize at the end
            params['ids'] = ",".join(batch)
            response = requests.get(url_base, params=params)
            records = json.loads(response.text)['records']

            for record in records:
                doi = record['doi']
                df.loc[doi, 'ncbi_ts'] = now

                if 'pmid' in record.keys():
                    df.loc[doi, 'pmid'] = record['pmid']

                if 'pmcid' in record.keys():
                    df.loc[doi, 'pmc'] = record['pmcid'][3:]

                if 'errmsg' in record.keys():
                    df.loc[doi, 'ncbi_errmsg'] = record['errmsg']

        # resolve doi's
        df['doi_url'] = None
        df['doi_resolve_ts'] = None
        df['doi_resolve_status'] = None
        df['doi_resolve_error'] = None
        timeout = 5

        for doi in df.index:
            now = datetime.datetime.now()

            # Init row values
            doi_resolve_status = None
            doi_resolve_error = None
            doi_url = None

            # Resolve DOI
            try:
                response = requests.get('https://doi.org/{}'.format(doi), allow_redirects=True, timeout=timeout)
                if response.ok:
                    doi_resolve_status = response.status_code
                    doi_url = response.url
                else:
                    response.urdoi_resolve_status = response.status_code
                    doi_resolve_error = response.reason
            except requests.exceptions.Timeout as ex:
                doi_resolve_error = "Timeout"
            except requests.exceptions.TooManyRedirects as ex:
                doi_resolve_error = "TooManyRedirects"
            except requests.exceptions.RequestException as ex:
                doi_resolve_error = "RequestException"

            df.loc[doi, 'doi_url'] = doi_url
            df.loc[doi, 'doi_resolve_status'] = doi_resolve_status
            df.loc[doi, 'doi_resolve_error'] = doi_resolve_error
            df.loc[doi, 'doi_resolve_ts'] = now
        print(df[:5])

        # save data to database
        num_added = 0
        num_already_in = 0
        for index, row in df.iterrows():
            print(index)
            result = Publication.query.filter_by(url=row['url'], doi=index).first()
            if result is None:
                pub = Publication(
                    url=row['url'],
                    doi=row['doi'],
                    date=row['date'],
                    pmid=row['pmid'],
                    pmc=row['pmc'],
                    ncbi_ts=row['ncbi_ts'],
                    ncbi_errmsg=row['ncbi_errmsg'],
                    doi_url=row['doi_url'],
                    doi_resolve_status=row['doi_resolve_status'],
                    doi_resolve_error=row['doi_resolve_error'],
                    doi_resolve_ts=row['doi_resolve_ts']
                )
                db.session.add(pub)
                num_added += 1
            else:
                num_already_in += 1
        db.session.commit()
        print(num_added, ' publications added to database.')
        print(num_already_in, ' publications already in database.')


class FacebookRequest(Command):
    """ Runs the Facebook Open Graph API request.

    """

    def run(self):
        print("hello world")


class AltmetricsRequest(Command):
    """ Runs the Altmetrics API request.

    """

    def run(self):
        print("hello world")


class ExportData(Command):
    """ Exports all stored data.

    """

    def run(self):
        print("hello world")


class ExportAltmetrics(Command):
    """ Exports the Altmetrics response data.

    """

    def run(self):
        print("hello world")


class ExportFacebook(Command):
    """ Exports the Facebook response data.

    """

    def run(self):
        print("hello world")


class ExportCrossRef(Command):
    """ Pushes the data to the CrossRef API.

    """

    def run(self):
        print('Hello')


if __name__ == "__main__":
    manager.add_command('create_db', CreateDb())
    # manager.add_command('drop_db', DropDb())
    manager.add_command('import_csv', ImportCsv())
    manager.add_command('request_facebook', FacebookRequest())
    manager.add_command('request_altmetrics', AltmetricsRequest())
    manager.add_command('export_data', ExportData())
    manager.add_command('export_altmetrics', ExportAltmetrics())
    manager.add_command('export_facebook', ExportFacebook())
    manager.add_command("runserver", Server())
    manager.add_command("show-urls", ShowUrls())
    manager.add_command("clean", Clean())
    manager.run()
