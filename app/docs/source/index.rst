.. _homepage:

Facebook Hidden Engagement Microservice (FHE Collector)
==================================================================================

Release v\ |version|.

.. image:: https://travis-ci.org/ScholCommLab/fhe-collector.svg?branch=master
    :target: https://travis-ci.org/ScholCommLab/fhe-collector

.. image:: https://readthedocs.org/projects/fhe-collector/badge/?version=latest
    :target: https://fhe-collector.readthedocs.io/en/latest

.. image:: https://coveralls.io/repos/github/ScholCommLab/fhe-collector/badge.svg
    :target: https://coveralls.io/github/ScholCommLab/fhe-collector

.. image:: https://img.shields.io/github/license/ScholCommLab/fhe-collector.svg
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

-------------------

.. _homepage_description:

The **Facebook Hidden Engagement Collector (FHE Collector)** is a Flask
application, which collects Facebook engagement metrics for scientific publication URL's.

**What does it do?**

FHE Collector collects Facebook engagement information for articles published
with `PKP's <https://pkp.sfu.ca>`_ Open Journal Systems (see
`https://pkp.sfu.ca/ojs/ <https://pkp.sfu.ca/ojs/>`_) on the level of
individual URLs and pushed these observations to
`Crossref Event Data <https://www.crossref.org/services/event-data/>`_.

The app takes a list of DOI's from a CSV-file and creates different kind of
URI's from it  both stored in the database. With these URI's a
Facebook openGraph API request is been made, where it gets a
Facebook openGraph object as a response. Then the relevant metrics get
extracted and stored in the database.

**What does it not do?**

- Aggregation of metrics
- Provide an endpoint to access metrics

Both aggregation of metrics and the access to the data are available through
Paperbuzz (which in turn aggregates events data from Crossref).

**What is Crossref Event Data?**

Crossref also collects _events_ related to DOIs which can be likes, shares,
comments, annotations. These observations are then open for interpretation
by endusers. See the
`Crossref Documentation <https://www.crossref.org/services/event-data/>`_
for more information.

**Resources**

- To read more about the difference between engagement data collected through the Facebook Graph API and approaches counting engagement on public posts see Enkhbayar & Alperin (2018). PDF available on `arXiv <https://arxiv.org/pdf/1809.01194.pdf>`_.
- Working document for the integration of Facebook-OJS into CED: (`GDoc <https://docs.google.com/document/d/10gjV8A8UgDOOM52ByTsaAvgzqLZtC2b6c_pnDEzBraI/edit?usp=sharing>`_))
- Code base for collecting URLs and engagement: `fhe-plos <https://github.com/ScholCommLab/fhe-plos>`_
- `Facebook API restrictions <https://newsroom.fb.com/news/2018/04/restricting-data-access/>`_


Developed by `Stefan Kasberger <http://stefankasberger.at>`_ and
`Asura Enkhbayar <https://github.com/Bubblbu>`_ for the
`Simon Fraser University - Scholarly Communication Lab <https://www.scholcommlab.ca/>`_.


.. _homepage_install:

Install
-----------------------------


.. code-block:: shell

    pip install fhe_collector


Find more options at :ref:`user_installation`.

**Requirements**

.. include:: snippets/requirements.rst


.. _homepage quickstart:

Quickstart
-----------------------------


.. _homepage_features:

Features
-----------------------------

- Python >=3.6
- Tested (`Travis CI <https://travis-ci.org/ScholCommLab/fhe-collector>`_) and documented (`Read the Docs <https://fhe-collector.readthedocs.io>`_)
- Open Source (`MIT <https://opensource.org/licenses/MIT>`_)


.. _homepage_user-guide:

User Guide
-----------------------------

.. toctree::
   :maxdepth: 3

   user/installation
   user/basic-usage
   user/resources


.. _homepage_reference:

Reference / API
-----------------------------

If you are looking for information on a specific class, function, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   reference

.. _homepage_community-guide:

Community Guide
-----------------------------

This part of the documentation, which is mostly prose, details the
FHE Collector ecosystem and community.

.. toctree::
   :maxdepth: 1

   community/faq
   community/contact
   community/releases


.. _homepage_contributor-guide:

Contributor Guide
-----------------------------

.. toctree::
   :maxdepth: 2

   contributing/contributing


.. _homepage_thanks:

Thanks!
-----------------------------

To everyone who has contributed to FHE Collector - with an idea, an issue, a
pull request, sharing it with others or by any other means:
Thank you for your support!

Open Source projects in general live from the cooperation of the many and it's projects are
standing on the shoulders of so many contributors, so to say thanks is the
least that can be done.

FHE Collector is funded by `Simon Fraser University - Scholarly Communication Lab <https://www.scholcommlab.ca/>`_


.. _homepage_license:

License
-----------------------------

Copyright Stefan Kasberger and others, 2021.

Distributed under the terms of the MIT license, FHE Collector is free and open source software.

Full License Text: `LICENSE.txt <https://github.com/ScholCommLab/fhe-collector/blob/master/LICENSE.txt>`_

The documentation is licensed under `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_.
