# Facebook Hidden Engagement Microservice

Simon Fraser University - Scholarly Communication Lab

Developed by [Stefan Kasberger](http://stefankasberger.at) and [Asura Enkhbayar](https://github.com/Bubblbu).

[![Build Status](https://travis-ci.org/ScholCommLab/fhe-collector.svg?branch=master)](https://travis-ci.org/ScholCommLab/fhe-collector)

[![Coverage Status](https://coveralls.io/repos/github/ScholCommLab/fhe-collector/badge.svg?branch=master)](https://coveralls.io/github/ScholCommLab/fhe-collector?branch=master)

**Features**

* Tests in [pytest-flask](http://pytest-flask.readthedocs.io/) and executed on [Travis CI](https://travis-ci.org/ScholCommLab/fhe-collector). Test coverage through [pytest-cov](https://pypi.org/project/pytest-cov/) and [python-coveralls](https://github.com/z4r/python-coveralls), viewable on (see [coveralls.io](https://coveralls.io/github/ScholCommLab/fhe-collector?branch=master)).
* auto-generated documentation through functions and class documentation with [sphinx](http://www.sphinx-doc.org/).

## SETUP

**Prerequisites**

* registered Facebook app
* Configured server, which can deliver Flask apps

**Download Flask app**

```
cd /PATH/TO/VHOST
git clone https://github.com/ScholCommLab/fhe-collector.git
cd fhe-collector
```

**Setup virtualenv**

```
virtualenv --python=/usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

**Create postgreSQL databse**

Write your usernames inside the quotations.

```
USERNAME_ADMIN=''
USERNAME_OWNER=''
sudo -u $USERNAME_ADMIN createdb -O $USERNAME_OWNER fhe_collector
```

**Initialize database**

```
flask db init
```

**User and database settings**

Rename the [settings_user_sample.py](settings_user_sample.py) file to 'settings_user.py' and add the missing user settings:

* facebook app
* flask app secret key
* NCBI API account

Also rename the [settings_production_sample.py](settings_production_sample.py) file to 'settings_production.py' and add the missing database settings:

Then set these environment variables inside your shell, so the right settings file is loaded when the app starts. There are three application modes:

* 'development':
* 'testing':
* 'production':

```
export FLASK_APP=fhe.py
export YOURAPPLICATION_MODE='development'
```

**Start app**

```
flask run
```

## Development

### Database Migration

```
flask db migrate -m "COMMENT"
flask db upgrade
```

### Testing

**pytest**

```
pytest
```

**Coverage**

```
coverage run fhe.py  
coverage report -m
coverage html
```

Run tests with coverage.
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

```
cd docs/
sphinx-build -b html docs/source docs/build
sphinx-apidoc -f -o source ../app
make html
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
