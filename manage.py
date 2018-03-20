import pandas as pd
import numpy as np
import re
import datetime
import time
import sys
import json
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
        df = df.drop_duplicates()
        for index, row in df.iterrows():
            result = Publication.query.filter_by(url=row['url'], doi=row['doi']).first()
            if result is None:
                pub = Publication(url=row['url'], doi=row['doi'], date=row['date'])
                db.session.add(pub)
                print('Add new publication to database.')
            else:
                print('Publication already in database.')
        db.session.commit()


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
