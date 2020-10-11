[![Build Status](https://travis-ci.org/ScholCommLab/fhe-collector.svg?branch=master)](https://travis-ci.org/ScholCommLab/fhe-collector) [![Coverage Status](https://coveralls.io/repos/github/ScholCommLab/fhe-collector/badge.svg?branch=master)](https://coveralls.io/github/ScholCommLab/fhe-collector?branch=master) [![Documentation Status](https://readthedocs.org/projects/fhe-collector/badge/?version=latest)](https://fhe-collector.readthedocs.io/en/latest/) [![GitHub](https://img.shields.io/github/license/ScholCommLab/fhe-collector.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Facebook Hidden Engagement Microservice

Simon Fraser University - Scholarly Communication Lab

Developed by [Stefan Kasberger](http://stefankasberger.at) and [Asura Enkhbayar](https://github.com/Bubblbu).

**Features**

* Tests written in [pytest-flask](http://pytest-flask.readthedocs.io/) and executed with [Travis CI](https://travis-ci.org/ScholCommLab/fhe-collector). Test coverage by [pytest-cov](https://pypi.org/project/pytest-cov/) and [python-coveralls](https://github.com/z4r/python-coveralls), viewable on [coveralls.io](https://coveralls.io/github/ScholCommLab/fhe-collector?branch=master).
* auto-generated documentation through functions and class documentation with [sphinx](http://www.sphinx-doc.org/).

**Copyright**

* Code:  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
* Documentation:  [![License: CC BY 4.0](https://licensebuttons.net/l/by/4.0/80x15.png)](https://creativecommons.org/licenses/by/4.0/)

## SETUP

This instructions are to setup the development environment, which is also the default environment.

**Prerequisites**

* Registered Facebook app
* Configured server, which can deliver a Flask app: we recommend using our [Docker-Container](https://github.com/skasberger/docker_fhe-collector) for this.

### PostgreSQL

**Install postgreSQL and create app database**

If you want to use postgreSQL as your primary database, execute the following commands. If not, the app will default to SQLite. We recommend using postgreSQL as your standard database, cause we experienced some issues with SQLite during development.

First, setup a postgreSQL instance on your computer. Please look for more information at the [PostgreSQL Website](https://www.postgresql.org).

*Create fhe_collector database*

After you have setup PostgreSQL, you have to create a database called `fhe_collector` and give your default user the full rights to it. In Ubuntu/Linux this works like this:
```
USERNAME_ADMIN='YOURADMINUSERNAME'
USERNAME_OWNER='YOUROWNERUSERNAME'
sudo -u $USERNAME_ADMIN createdb -O $USERNAME_OWNER fhe_collector
```

*Pass PostgreSQL database URI*

If you want to use a custom SQL-Alchemy database connection, you can pass the proper string via an environment variable. For more information about this, look at [SLQAlchemy](https://www.sqlalchemy.org/). Beware, that you need the username - maybe with a password - who can execute queries in it.

```bash
export SQLALCHEMY_DATABASE_URI='postgresql://localhost/fhe_collector'
```

**Initialize database**

```bash
flask db init
```

**Upgrade database**

```bash
flask db upgrade
```

**User and database settings**

Rename the [app/settings_sample.json](app/settings_sample.json) file to `settings_INSTANCE.json` and add the missing user settings in it. Replace "INSTANCE" with a fitting name (e. g. `production`, `development`).

### FHE Collector

**Download FHE Collector**

Get the app on your computer, into your webservers directory (e. g. vhost).

```bash
cd /PATH/TO/VHOST
git clone https://github.com/ScholCommLab/fhe-collector.git
cd fhe-collector
```

**Install requirements**

Start the virtual environment to install the needed python packages.

```bash
pip install -r requirements.txt
```

**Set environment variables**

* `FLASK_APP`: name of the initial app python file, in our case `main`.
* `FLASK_ENV`: `development` or `production`
* `SQLALCHEMY_DATABASE_URI`: Database URI for SQLAlchemy.
* `YOURAPPLICATION_SETTINGS`: name of instance settings (must be inside `app/`).

Example:

```bash
export FLASK_APP="main"
export FLASK_ENV=development
export SQLALCHEMY_DATABASE_URI="postgresql://localhost/fhe_collector"
export YOURAPPLICATION_SETTINGS="settings_development.json"
```

**Run**

Run the flask app:

```bash
flask run
```

## COMMANDS

You can find all commands listed up via `flask --help` and in the file `main.py`.

To execute flask commands, the following pattern is used:

```bash
flask COMMAND <OPTIONAL>
```

Commands offered:

* `init`: Initialize data at the beginning.
  * `filename`: CSV filename to be imported (optional).
* `doi-new`: Create all new DOI URL's.
* `doi-old`: Create all old DOI URL's.
* `doi-lp`: Create all DOI Landing Page URL's.
* `ncbi`: Create all NCBI URL's.
* `unpaywall`: Create all Unpaywall URL's.
* `fb`: Get all Facebook data.
* `res-tables`: Delete and create empty tables.
* `imp`: Import the tables.
  * `table_names`: String with table names, separated by comma.
  * `import_type`: `append` to add data to the existing or `reset` to re-create the tables.
* `exp`: Export the tables.
  * `table_names`: String with table names, separated by comma.
* `db`: Run database commands.
* `run`: Run the Flask app on your production or development server.
* `shell`: get inside the Flask shell.

For more details on each command, look inside the code documentation.

## Development

**Install**

```bash
cd /PATH/TO/VHOST
git clone https://github.com/ScholCommLab/fhe-collector.git
cd fhe-collector
python3 -m venv venv
source venv/bin/activate
pip install tox
pip install -r requirements.txt
pip install -r deps/dev-requirements.txt
pre-commit install
```

### Database Migration

After changing your SQLAlchemy models, you have to update your database. To add information about your changes, exchange "COMMENT" with your commit message.

```
flask db migrate -m "COMMENT"
flask db upgrade
```

### Testing

To execute the tests, set the application mode and unset database URI.

```
unset SQLALCHEMY_DATABASE_URI
```

**tox**

To execute the tests with tox (as recommended), simply type:
```
tox
```

You can find out more about the tox configuration inside `tox.ini` and in its [documentation](https://tox.readthedocs.io).

**Coverage**

To get test coverage of codebase, use coverage.

```
coverage run fhe.py
coverage report -m
coverage html
```

Run tests with coverage to create a html report as an output.

```
pytest --cov-report html --cov=app tests/
```
**Coveralls**

To use Coveralls on local development:
```
pytest tests/ --doctest-modules -v --cov=app
```

And to use Coveralls on Travis-CI
```
pytest tests/ --doctest-modules -v --cov coveralls --cov-report term-missing
```

### Documentation

Use Sphinx to create class and function documentation out of the doc-strings.

```
tox -e docs
```
