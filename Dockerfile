FROM tiangolo/meinheld-gunicorn-flask:python3.7

LABEL Version="0.1.0"
LABEL Description="FHE Collector docker container" License="MIT"
LABEL maintainer="Stefan Kasberger <mail@stefankasberger.at>"

# ENV GIT_COMMIT
ENV FLASK_CONFIG docker

RUN python -m pip install --upgrade pip

RUN git clone --single-branch --branch develop https://github.com/skasberger/fhe-collector /home/fhe_collector

RUN cp -r /home/fhe_collector/requirements .
RUN pip install -r requirements/docker.txt

RUN cp -r /home/fhe_collector/fhe_collector .
RUN cp -r /home/fhe_collector/migrations .
RUN rm -f main.py
RUN cp -f /home/fhe_collector/main.py .
RUN cp -f /home/fhe_collector/config.py .
RUN rm -f prestart.sh
