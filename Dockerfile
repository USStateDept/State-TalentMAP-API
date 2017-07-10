FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Note that we want postgresql-client so 'manage.py dbshell' works.
RUN apt-get update && apt-get install -y postgresql-client

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app/
RUN pip install -r requirements.txt
