FROM python:3.7.5

ENV PYTHONUNBUFFERED 1

# Installing Oracle instant client
WORKDIR    /opt/oracle
RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-basiclite-linux.x64-19.8.0.0.0dbru.zip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-sdk-linux.x64-19.8.0.0.0dbru.zip \
            && unzip instantclient-basiclite-linux.x64-19.8.0.0.0dbru.zip \
            && unzip instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip \
            && unzip instantclient-sdk-linux.x64-19.8.0.0.0dbru.zip \
            && rm -f instantclient-basiclite-linux.x64-19.8.0.0.0dbru.zip \
            && rm -f instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip \
            && rm -f instantclient-sdk-linux.x64-19.8.0.0.0dbru.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

# We want xmlsec1 to support SAML SSO
RUN apt-get update && apt-get install -y xmlsec1
# You may need all of these to use SSO - yum install libffi-devel xmlsec1 xmlsec1-openssl

RUN mkdir /app
RUN mkdir /app/logs
RUN mkdir /var/log/talentmap/ && chmod a+wrxs /var/log/talentmap/

ADD requirements.txt /app/
ADD requirements-no-deps.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install -r requirements-no-deps.txt --no-dependencies

COPY talentmap_api /app/talentmap_api/
ADD wait-for-oracle.sh create-oracle-user.sh manage.py setup.cfg show_logo.py /app/

RUN chmod +x wait-for-oracle.sh
RUN chmod +x create-oracle-user.sh
