FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Note that we want postgresql-client so 'manage.py dbshell' works.
RUN apt-get update && apt-get install -y postgresql-client

RUN mkdir /app
WORKDIR /app

ADD . /app/
RUN chmod +x wait-for-postgres.sh
RUN pip install -r requirements.txt
