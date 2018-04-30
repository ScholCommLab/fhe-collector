# Facebook Hidden Engagement Microservice

Simon Fraser University - Scholarly Communication Lab

Developed by [Stefan Kasberger](http://stefankasberger.at) and [Asura Enkhbayar](https://github.com/Bubblbu).

[![Build Status](https://travis-ci.org/ScholCommLab/fhe-collector.svg?branch=master)](https://travis-ci.org/ScholCommLab/fhe-collector)

## SETUP

**Download**

```
cd /PATH/TO/VHOST
git clone https://github.com/ScholCommLab/fhe-collector.git
cd fhe-microservice
```

**virtualenv**

```
virtualenv --python=/usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

**postgreSQL**
```
USERNAME_ADMIN=''
USERNAME_OWNER=''
sudo -u $USERNAME_ADMIN createdb -O $USERNAME_OWNER myProject_myApp
```

**testing installation**

# Development

## localhost

```
```

```
coverage run --source='.'
coverage report
```
