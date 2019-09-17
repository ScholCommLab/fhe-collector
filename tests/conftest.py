# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/ScholCommLab/fhe-collector."""
from app import create_app
import os
import pytest

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


# @pytest.fixture
# def app():
#     os.environ['ENV'] = 'development'
#     app = create_app({
#         'TESTING': True,
#         'ENV': 'development'
#     })
#     with app.app_context():
#         app.db.init_db()
#     yield app


# @pytest.fixture
# def client(app):
#     return app.test_client()


# @pytest.fixture
# def runner(app):
#     return app.test_cli_runner()


@pytest.fixture
def import_ncbi():
    """Import DOI list for NCBI Requests.

    Returns
    -------
    list
        List of tuples with (doi, result)

    """
    # ncbi_url, pm_id, pmc_id
    data = [
        ('10.1371/journal.pone.0141854', '26540108', 'PMC4634878', 'ok'),
        ('10.1371/journal.pone.0149989', '27008093', 'PMC4805169', 'ok'),
        ('10.1371/journal.pone.0153419', '27128318', 'PMC4851308', 'ok'),
        ('10.1371/journal.pone.0146193', '26730579', 'PMC4701170', 'ok'),
        ('10.1371/journal.pone.0185809', '29045418', 'PMC5646769', 'ok'),
        ('10.22230/src.2010v1n1a3', '29045418', 'PMC5646769', 'error')
    ]
    return data


@pytest.fixture
def import_doi_landingpage():
    """Import DOI list for NCBI Requests.

    Returns
    -------
    list
        List of tuples with (doi, result)

    """
    # ncbi_url, pm_id, pmc_id
    data = [
        ('10.1371/journal.pone.0141854', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0141854'),
        ('10.1371/journal.pone.0149989', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0149989'),
        ('10.1371/journal.pone.0153419', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0153419'),
        ('10.1371/journal.pone.0146193', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0146193'),
        ('10.22230/src.2010v1n1a3', 'https://src-online.ca/index.php/src/article/view/3')
    ]
    return data


@pytest.fixture
def import_unpaywall():
    """Import DOI list for NCBI Requests.

    Returns
    -------
    list
        List of tuples with (doi, result)

    """
    # ncbi_url, pm_id, pmc_id
    data = [
        (
            '10.1371/journal.pone.0141854',
            {
                'url': [
                    'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0141854&type=printable',
                    'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0149989&type=printable',
                    'https://doi.org/10.1371/journal.pone.0141854',
                    'http://europepmc.org/articles/pmc4634878?pdf=render',
                    'https://www.issuelab.org/permalink/resource/25187',
                    'https://doi.org/10.1371/journal.pone.0141854',
                    'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4634878'
                ],
                'url_for_landing_page': [
                    'https://doi.org/10.1371/journal.pone.0141854',
                    'http://europepmc.org/articles/pmc4634878',
                    'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4634878',
                    'https://www.issuelab.org/permalink/resource/25187'
                ],
                'url_for_pdf': [
                    'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0141854&type=printable',
                    'http://europepmc.org/articles/pmc4634878?pdf=render',
                    None
                ]
             },
            'ok'
         ),
        (
            '10.1371/journal.pone.0149989',
            [
                {
                    'url': 'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0141854&type=printable',
                    'url_for_landing_page': 'https://doi.org/10.1371/journal.pone.0149989',
                    'url_for_pdf': 'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0149989&type=printable'
                 },
                {
                    'url': 'https://doi.org/10.1371/journal.pone.0149989',
                    'url_for_landing_page': 'https://doi.org/10.1371/journal.pone.0149989',
                    'url_for_pdf': None
                 },
                {
                    'url': 'http://europepmc.org/articles/pmc4805169?pdf=render',
                    'url_for_landing_page': 'http://europepmc.org/articles/pmc4805169',
                    'url_for_pdf': 'http://europepmc.org/articles/pmc4805169?pdf=render'
                 },
                {
                    'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4805169',
                    'url_for_landing_page': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4805169',
                    'url_for_pdf': None
                 }
            ],
            'ok'
         ),
        (
            '10.22230/src.2010v1n1a3',
            [
                {
                    'url': 'https://src-online.ca/index.php/src/article/download/3/20',
                    'url_for_landing_page': 'https://doi.org/10.22230/src.2010v1n1a3',
                    'url_for_pdf': 'https://src-online.ca/index.php/src/article/download/3/20'
                 }
            ],
            'ok'
         )
        # (
        #     '',
        #     [
        #         {
        #             'url': '',
        #             'url_for_landing_page': '',
        #             'url_for_pdf': ''
        #          },
        #         {
        #             'url': '',
        #             'url_for_landing_page': '',
        #             'url_for_pdf': ''
        #          },
        #         {
        #             'url': '',
        #             'url_for_landing_page': '',
        #             'url_for_pdf': ''
        #          },
        #         {
        #             'url': '',
        #             'url_for_landing_page': '',
        #             'url_for_pdf': ''
        #          }
        #     ],
        #     'ok'
        #  ),
    ]
    return data
