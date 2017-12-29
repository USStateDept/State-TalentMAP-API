#!/bin/bash

# The database to connect to
export DATABASE_URL='postgres://username:password@hostname:5432/database_name'

# The Django secret key
export DJANGO_SECRET_KEY='secret_key'

# Set the debug setting (True, true, or 1)
# This should be set to False when in deployment
export DJANGO_DEBUG=True

# Deployment location
# The directory where manage.py is located; requires the trailing slash
export DEPLOYMENT_LOCATION='/var/www/talentmap/api/'


# SOAP API
export WSDL_LOCATION='http://www.webservicex.net/uszip.asmx?WSDL'
