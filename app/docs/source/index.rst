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

The Facebook Hidden Engagement Collector is a Flask application, which collects Facebook engagement metrics for scientific publication URL's.


Developed by `Stefan Kasberger <http://stefankasberger.at>`_ and `Asura Enkhbayar <https://github.com/Bubblbu>`_ for the Simon Fraser University - `Scholarly Communication Lab <https://www.scholcommlab.ca/>`_.


.. _homepage features:

Features
-----------------------------

- Python >=3.6
- Tests with `Travis CI <https://travis-ci.org/ScholCommLab/fhe-collector>`_ (`pytest-flask <https://pytest-flask.readthedocs.io/en/latest/>`_ + `tox <http://tox.readthedocs.io/>`_)
- Auto-generated documentation with `sphinx <http://www.sphinx-doc.org/>`_.
- Open Source (`MIT <https://opensource.org/licenses/MIT>`_)


.. _homepage install:

Install
-----------------------------

**Prerequisites**

* Registered Facebook app
* PostgreSQL

**Clone repository**

.. code-block:: shell

    git clone git@github.com:ScholCommLab/fhe-collector.git
    cd fhe-collector
    pip install .

**PostgreSQL**

First, setup a postgreSQL instance on your computer. Please look for 
more information at the `PostgreSQL Website <https://www.postgresql.org>`_.

After you have setup PostgreSQL, you have to create a database for the app and give 
your default user the full rights to it. In Ubuntu/Linux this works like this:

.. code-block:: shell

    USERNAME_ADMIN='YOURADMINUSERNAME'
    USERNAME_OWNER='YOUROWNERUSERNAME'
    DB_NAME='fhe_collector'
    sudo -u $USERNAME_ADMIN createdb -O $USERNAME_OWNER $DB_NAME


.. _homepage quickstart:

Quickstart
-----------------------------

**Settings**

There are 3 different configurations available:

- ``development``: for development purpose
- ``testing``: for testing (locally and travis)
- ``production``: for all production instances (docker and docker compose too)

You have to set the ``FLASK_CONFIG`` environment variable to tell the application, which one you want.

.. code-block:: shell

    export FLASK_CONFIG="development"


Each configuration looks by default for an ``.env``-file inside the folder ``env/``, 
if not otherwise told:

- ``development`` looks for ``env/development.env``
- ``testing`` looks for ``env/testing.env``
- ``production`` looks for ``env/production.env``

If you want to locate your ``.env``-file in another place, you can define the path with the environment 
variable ``ENV_FILE``. The filename must be absolute or relative to the location of ``config.py`` inside ``app/``.

.. code-block:: shell

    export ENV_FILE="/my/absolute/env/directory/filename.env"


The ``testing.env`` file is the only one available in the repository, all others must be created by yourself. We 
recommend to copy the testing.env and adapt it to your needs.

Environment variables:

- ``SQLALCHEMY_DATABASE_URI``: Database URI (required)
- ``SECRET_KEY``: Secret key for the flask application
- ``API_TOKEN``: API Token for client authentication
- ``ADMIN_EMAIL``: Email of app administrator
- ``APP_EMAIL``: Email of the app for the NCBI (PMC, PM) requests.
- ``NCBI_TOOL``: Name of the app for the NCBI (PMC, PM) requests.
- ``FB_APP_ID``: Facebook app ID
- ``FB_APP_SECRET``: secret token of Facebook app
- ``FB_HOURLY_RATELIMIT``: hourly ratelimit, how many requests should be made to the Facebook openGraph API

Hint: You can define all environment variables also in your shell. They will 
overwrite environment variables defined in ``.env``-files.

**Start app**

To start the app, you have to tell the server where to look for the created app. For this, set the ``FLASK_APP`` environment variable (e. g. the instance ``app`` inside the file ``main.py``):

.. code-block:: shell

    export FLASK_APP=main:app
    flask run

**Commands**

To execute flask commands, the following pattern is used:

.. code-block:: shell

    flask COMMAND <OPTIONAL>


All commands are listed up via ``--help``:

.. code-block:: shell

    flask run --help


.. _homepage development:

Development
-----------------------------

**Install**

Install from the local git repository, with all it's dependencies:

.. code-block:: shell

    git clone git@github.com:ScholCommLab/fhe-collector.git
    cd fhe-collector
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements/development.txt
    pip install -e .
    pre-commit install

**Testing**

To execute the tests with tox (as recommended), simply type:

.. code-block:: shell

    tox

You can find out more about the tox configuration inside ``tox.ini`` and the `tox documentation <https://tox.readthedocs.io>`_.

**Coverage**

Use coverage for this:

.. code-block:: shell

    tox -e coverage

Also coveralls is available:

.. code-block:: shell

    tox -e coveralls

**Docs**

Use sphinx to create the documentation:

.. code-block:: shell

    tox -e docs


**Linting**

mypy:

.. code-block:: shell

    tox -e mypy

pylint:

.. code-block:: shell

    tox -e pylint


**Code formatting**

black:

.. code-block:: shell

    tox -e black

.. _homepage references:


.. _homepage contribute:

Contribute
-----------------------------

In the spirit of free software, everyone is encouraged to help improve this project.

Here are some ways you can contribute:

- by reporting bugs
- by suggesting new features
- by translating to a new language
- by writing or editing documentation
- by writing code (**no pull request is too small**: fix typos in the user interface, add code comments, clean up inconsistent whitespace)
- by refactoring code or adding new features (please get in touch with us before you do, so we can syncronize the efforts and prevent misunderstandings)
- by `closing issues <https://github.com/ScholCommLab/fhe-collector/issues>`_
- by `reviewing pull requests <https://github.com/ScholCommLab/fhe-collector/pulls>`_

When you are ready, submit a `pull request <https://github.com/ScholCommLab/fhe-collector>`_.

**Submitting an Issue**

We use the `GitHub issue tracker <https://github.com/ScholCommLab/fhe-collector/issues>`_
to track bugs and features. Before submitting a bug report or feature request,
check to make sure it hasn't already been submitted. When submitting a bug report,
please try to provide a screenshot that demonstrates the problem.


Reference / API
-----------------------------

If you are looking for information on a specific class, function, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   reference

.. _homepage thank:

Thanks!
-----------------------------

To everyone who has contributed to FHE Collector - with an idea, an issue, a
pull request, sharing it with others or by any other means:
Thank you for your support!

Open Source projects in general live from the cooperation of the many and it's projects are
standing on the shoulders of so many contributors, so to say thanks is the
least that can be done.

FHE Collector is funded by Simon Fraser University - `Scholarly Communication Lab <https://www.scholcommlab.ca/>`_


.. _homepage license:

License
-----------------------------

Copyright Stefan Kasberger and others, 2018.

Distributed under the terms of the MIT license, FHE Collector is free and open source software.

Full License Text: `LICENSE.txt <https://github.com/ScholCommLab/fhe-collector/blob/master/LICENSE.txt>`_

The documentation is licensed under `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
