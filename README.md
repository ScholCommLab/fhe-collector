[![Build Status](https://travis-ci.org/ScholCommLab/fhe-collector.svg?branch=master)](https://travis-ci.org/ScholCommLab/fhe-collector) [![Coverage Status](https://coveralls.io/repos/github/ScholCommLab/fhe-collector/badge.svg?branch=master)](https://coveralls.io/github/ScholCommLab/fhe-collector?branch=master)

# Facebook Hidden Engagement Microservice

Simon Fraser University - Scholarly Communication Lab

Developed by [Stefan Kasberger](http://stefankasberger.at) and [Asura Enkhbayar](https://github.com/Bubblbu).

**Features**

* Tests wirtten in [pytest-flask](http://pytest-flask.readthedocs.io/) and executed with [Travis CI](https://travis-ci.org/ScholCommLab/fhe-collector). Test coverage by [pytest-cov](https://pypi.org/project/pytest-cov/) and [python-coveralls](https://github.com/z4r/python-coveralls), viewable on [coveralls.io](https://coveralls.io/github/ScholCommLab/fhe-collector?branch=master).
* auto-generated documentation through functions and class documentation with [sphinx](http://www.sphinx-doc.org/).

## SETUP

This instructions are to setup the development environment, which is also the default environment.

**Prerequisites**

* registered Facebook app
* Configured server, which can deliver a Flask app

**Download Flask app**

Get the app on your computer, into your webservers directory (e. g. vhost).

```
cd /PATH/TO/VHOST
git clone https://github.com/ScholCommLab/fhe-collector.git
cd fhe-collector
```

**Setup virtualenv**

Start the virtual environment to install the needed python packages.

```
virtualenv --python=/usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

**Install postgreSQL and create app databse**

If you want to use postgreSQL as your primary database, execute the following commands. If not, the app will default to SQLite. We recommend using postgreSQL as your standard database, cause we experienced some issues with SQLite during development.

First, setup a postgreSQL instance on your computer. Please look for more information at the [PostgreSQL Website](https://www.postgresql.org).

*Create fhe_collector database*

After you have setup PostgreSQL, you have to create a database called `fhe_collector` and give your default user the full rights to it. In Ubuntu this works like this:
```
USERNAME_ADMIN='YOURADMINUSERNAME'
USERNAME_OWNER='YOUROWNERUSERNAME'
sudo -u $USERNAME_ADMIN createdb -O $USERNAME_OWNER fhe_collector
```

*Pass PostgreSQL database URI*

If you want to use a custom SQL-Alchemy database connection, you can pass the proper string via an environment variable.
```
export SQLALCHEMY_DATABASE_URI='postgresql://localhost/fhe_collector'
```

**Initialize database**

```
flask db init
```

**User and database settings**

Rename the [settings_user_sample.py](settings_user_sample.py) file to `settings_user.py` and add the missing user settings in it.

Then set the `YOURAPPLICATION_MODE` variable inside your shell, so the right settings file is loaded when the app starts. There are three application modes:

* 'DEVELOPMENT': is the default one. Does not need to be set, unless it does not work as expected.
* 'TESTING': to execute the tests.
* 'PRODUCTION': to run in production mode.

**Start app**

```
export FLASK_APP=fhe.py
flask run
```

## Development

### Database Migration

Update your database after changes.

```
flask db migrate -m "COMMENT"
flask db upgrade
```

### Testing

Execute the test-scripts.

```
export FLASK_APP=fhe.py
export YOURAPPLICATION_MODE='TESTING'
export SQLALCHEMY_DATABASE_URI='postgresql://localhost/fhe_collector'
```

**pytest**

```
pytest
```

**Coverage**

Get test coverage of codebase.

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

Local development
```
pytest tests/ --doctest-modules -v --cov=app
```

Travis
```
pytest tests/ --doctest-modules -v --cov coveralls --cov-report term-missing
```

### Documentation

Use Sphinx to create class and function documentation out of the codebase.

```
cd docs/
sphinx-build -b html source build
sphinx-apidoc -f -o source ..
make html
```

## Production

To run the app on production, rename the [settings_production_sample.py](settings_production_sample.py) file to `settings_production.py` and add the missing database settings. Also set the `ỲOURAPPLICATION_MODE` to `development`.

```
export FLASK_APP=fhe.py
export YOURAPPLICATION_MODE='PRODUCTION'
```

## GLOSSAR

**Coverage.py**

Coverage.py is a tool for measuring code coverage of Python programs. It monitors your program, noting which parts of the code have been executed, then analyzes the source to identify code that could have been executed but was not. Coverage measurement is typically used to gauge the effectiveness of tests. It can show which parts of your code are being exercised by tests, and which are not.

**Coveralls.io**

Coveralls is a web service to help you track your code coverage over time, and ensure that all your new code is fully covered.

**Travis CI**

Travis CI is a hosted, distributed continuous integration service used to build and test software projects hosted at GitHub.

**Sphinx**

Sphinx is a tool that makes it easy to create intelligent and beautiful documentation. It can create reports in pdf and html.
