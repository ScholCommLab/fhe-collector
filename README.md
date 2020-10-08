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

* registered Facebook app
* Configured server, which can deliver a Flask app

**Download Flask app**

Get the app on your computer, into your webservers directory (e. g. vhost).

```bash
cd /PATH/TO/VHOST
git clone https://github.com/ScholCommLab/fhe-collector.git
cd fhe-collector
```

**Setup virtualenv**

Start the virtual environment to install the needed python packages.

```bash
virtualenv --python=/usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

**Install postgreSQL and create app databse**

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

Rename the [settings_user_sample.py](settings_user_sample.py) file to `settings_user.py` and add the missing user settings in it.

## Development

### Running

Before you can start here, you have to do all steps in the Setup section.

**Tell starting point of application**

```bash
export FLASK_APP=fhe.py
```

**Configure the environment**

Set the `ENV` variable and `DEBUG` to `true` if you are developing.

* `development`: is the default one. Does not need to be set, unless it does not work as expected.
* `testing`: to execute the tests.
* `production`: to run in production mode.

```bash
export ENV=development
export DEBUG=true
```

**Configure database**

Set your database. The following example show how to connect to your postgreSQL database `fhe_collector`.

```bash
export SQLALCHEMY_DATABASE_URI='postgresql://localhost/fhe_collector'
```

**Run**

Run the app as usual:

```bash
flask run
```

### Flask Commands

To execute flask commands in the shell, the following pattern is used:

```bash
flask COMMAND <OPTIONAL>
```

Commands offered:

* `init_data`
* `delete_init`
* `reset_init`
* `delete_dois`
* `create_doi_urls`
* `create_doi_new_urls`
* `create_doi_old_urls`
* `create_doi_lp_urls`
* `create_ncbi_urls`
* `create_unpaywall_urls`
* `delete_urls`
* `delete_apirequests`
* `create_fbrequests`
* `delete_fbrequests`
* `delete_data`
* `reset_data`
* `export_tables`
* `import_tables`

For more details on each command, look inside the code documentation.

### Database Migration

After changing your SQLAlchemy models, you have to update your database. To add information about your changes, exchange "COMMENT" with your commit message.

```
flask db migrate -m "COMMENT"
flask db upgrade
```

### Testing

To execute the tests, set the application mode and unset database URI.

```
export FLASK_APP=fhe.py
export ENV=testing
```

If you set the database URI as an environment variable and you don't want to use it anymore, simply unset it.

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

## Production

To run the app on production, rename the [settings_production_sample.py](settings_production_sample.py) file to `settings_production.py` and add the missing database settings. Also set the `ỲOURAPPLICATION_MODE` to `development`.

```
export FLASK_APP=fhe.py
export ENV=production
flask run
```
