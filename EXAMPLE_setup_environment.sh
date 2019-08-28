#!/bin/bash

# Note that this file is parsed by python (in wsgi.py) so do not use any
# interpolated bash variables; like $HOME

# This is used to ensure environment variables don't conflict when ready by WSGI
export DJANGO_ENVIRONMENT_NAME='environment1'

# The database to connect to
export DATABASE_URL='postgres://username:password@hostname:5432/database_name'

# The Django secret key
export DJANGO_SECRET_KEY='secret_key'

# Set the debug setting (True, true, or 1)
# This should be set to False when in deployment
export DJANGO_DEBUG=True

# Logging Configuration
# Base logging directory
# Ensure this directory is writable/creatable by the Apache process, and that new
# files in that directory inherit that permission structure (chmod +s) or that it
# is entirely owned by the Apache process. Don't forget the trailing slash
export DJANGO_LOG_DIRECTORY='/var/log/talentmap/'

# The following environment variables define the name and logging specifications for
# each file. The defaults should be sufficient, but you may change them here if needed
#  NAME - the name of the file
#  MAX_SIZE - the max size of the file before rotating (in bytes)
#  NUM_BACKUPS - the number of backups to keep before deletion

# Auth Logging
# Stores authentication requests
export DJANGO_LOG_AUTH_NAME='auth.log'

# Access logging
# Stores all requests
export DJANGO_LOG_ACCESS_NAME='access.log'

# Generic logging
# Stores all logging which lies outside of other specific logs, such as profile
# modifications, saving favorites, etc...
export DJANGO_LOG_GENERIC_NAME='talentmap.log'

# Permission logging
# Stores any permission changes
export DJANGO_LOG_PERM_NAME='permissions.log'

# Database logging
# Stores every SQL command sent to the database; Please note this only functions with DEBUG set to true
export DJANGO_LOG_DB_NAME='db.log'

# Synchronization logging
# Stores synchronization data
export DJANGO_LOG_SYNC_NAME='sync.log'

# Deployment location
# The directory where manage.py is located; requires the trailing slash
export DEPLOYMENT_LOCATION='/var/www/talentmap/api/'

# SOAP API
export WSDL_LOCATION='http://www.webservicex.net/uszip.asmx?WSDL'
# The location of a certificate to verify self-signed SSL certificates on the WSDL (optional)
export WSDL_SSL_CERT=''
# You may set any number of soap headers as key=value pairs, in variables starting with DJANGO_SOAP_HEADER
export DJANGO_SYNCHRONIZATION_HEADER_ANY_STRING="x-key-here=value"
# You may set any number of namespace overrides for the SOAP XML here (from=to format)
export DJANGO_SOAP_NS_OVERRIDE_ANY_STRING="ns0=tem"
export SOAP_TIMEOUT=180
export SOAP_MAX_ATTEMPTS=5

# SAML2 Configuration
export ENABLE_SAML2=False
# SAML2 debug setting, 1 or 0
export SAML2_DEBUG=1

# Node settings
export NODE_TLS_REJECT_UNAUTHORIZED=0
# Redirect url
export SAML_LOGIN_REDIRECT_URL="https://somewhere"
# Front end ACS binding for SAML redirects to ACS
export FRONT_END_ACS_BINDING="https://somewhere"
# This setting controls whether the session expires when the user closes the browser
export SAML2_SESSION_EXPIRE_AT_BROWSER_CLOSE=True
# The location of the xmlsec1 binary
export SAML2_XMLSEC1_PATH='/usr/bin/xmlsec1'
# The location of the machine running as the service provider (i.e. this deployment) on the network
# Please include the trailing slash
export SAML2_NETWORK_LOCATION='https://localhost:8080/'
# IDP data
export SAML2_IDP_METADATA_ENDPOINT='https://localhost/simplesaml/saml2/idp/metadata.php'
export SAML2_IDP_SSO_LOGIN_ENDPOINT='https://localhost/simplesaml/saml2/idp/SSOService.php'
export SAML2_IDP_SLO_LOGOUT_ENDPOINT='https://localhost/simplesaml/saml2/idp/SingleLogoutService.php'
# Certs and Keys
# Signing
export SAML2_SIGNING_KEY='/home/talentmap/signing_talentmap.key'
export SAML2_SIGNING_CERT='/home/talentmap/signing_talentmap.pem'
# Encryption
export SAML2_ENCRYPTION_KEY='/home/talentmap/encrypt_talentmap.key'
export SAML2_ENCRYPTION_CERT='/home/talentmap/encrypt_talentmap.pem'
# SAML2 Metadata
export SAML2_TECHNICAL_POC_FIRST_NAME=''
export SAML2_TECHNICAL_POC_LAST_NAME=''
export SAML2_TECHNICAL_POC_COMPANY=''
export SAML2_TECHNICAL_POC_EMAIL=''
export SAML2_ADMINISTRATIVE_POC_FIRST_NAME=''
export SAML2_ADMINISTRATIVE_POC_LAST_NAME=''
export SAML2_ADMINISTRATIVE_POC_COMPANY=''
export SAML2_ADMINISTRATIVE_POC_EMAIL=''

export FSBID_API_URL='http://mock_fsbid:3333'
export OBC_URL='http://localhost:4000'
