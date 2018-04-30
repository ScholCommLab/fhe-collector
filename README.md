# Facebook Hidden Engagement Microservice

Simon Fraser University - Scholarly Communication Lab

Developed by [Stefan Kasberger](http://stefankasberger.at) and [Asura Enkhbayar](https://github.com/Bubblbu).

[![Build Status](https://travis-ci.org/ScholCommLab/fhe-collector.svg?branch=master)](https://travis-ci.org/ScholCommLab/fhe-collector)

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

**Set settings**

Rename the [settings_production_sample.py](settings_production_sample.py) file to 'settings_production.py' and add the missing information about:

* postgresql database
* facebook app
* flask app secret key

Then set these environment variables inside your shell, so the right settings file is used to run the app.

```
export FLASK_APP=fhe.py
export YOURAPPLICATION_SETTINGS='/PATH/TO/VHOST/fhe-collector/settings_production.py'
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

```
pytest
```

```
coverage run --source='.'
coverage report
```
