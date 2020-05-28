FROM python:3.7.5

ENV PYTHONUNBUFFERED 1

# Installing Oracle instant client
WORKDIR    /opt/oracle
RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-sqlplus-linux.x64-19.6.0.0.0dbru.zip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-sdk-linux.x64-19.6.0.0.0dbru.zip \
            && unzip instantclient-basiclite-linuxx64.zip \
            && unzip instantclient-sqlplus-linux.x64-19.6.0.0.0dbru.zip \
            && unzip instantclient-sdk-linux.x64-19.6.0.0.0dbru.zip \
            && rm -f instantclient-basiclite-linuxx64.zip \
            && rm -f instantclient-sqlplus-linux.x64-19.6.0.0.0dbru.zip \
            && rm -f instantclient-sdk-linux.x64-19.6.0.0.0dbru.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

# Note that we want postgresql-client so 'manage.py dbshell' works.
# We want xmlsec1 to support SAML SSO
RUN apt-get update && apt-get install -y postgresql-client xmlsec1

RUN mkdir /app
RUN mkdir /app/logs
RUN mkdir /var/log/talentmap/ && chmod a+wrxs /var/log/talentmap/

ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

COPY talentmap_api /app/talentmap_api/
ADD wait-for-it.sh wait-for-postgres.sh manage.py setup.cfg show_logo.py /app/

RUN chmod +x wait-for-it.sh
RUN chmod +x wait-for-postgres.sh
