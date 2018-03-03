#!/bin/bash

# Note that this file is parsed by python (in wsgi.py) so do not use any
# interpolated bash variables; like $HOME


# The database to connect to
export DATABASE_URL='postgres://username:password@hostname:5432/database_name'

# The Django secret key
export DJANGO_SECRET_KEY='secret_key'

# Set the debug setting (True, true, or 1)
# This should be set to False when in deployment
export DJANGO_DEBUG=True

# The debug log destination; either 'console' or 'file'
# The file output will be located in logs/debug.log; ensure proper permissions are set
export DEBUG_LOG_DESTINATION='console'

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
