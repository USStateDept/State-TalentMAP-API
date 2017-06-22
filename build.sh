#!/bin/bash

set -e

pip install virtualenv
virtualenv talentmap-env
source talentmap-env/bin/activate

# Set environment variables
export DATABASE_URL="postgresql://user:pass@url.com/data_base_name"
export DJANGO_SECRET="someRandomString"
# For dev/stg debug on is probably advisable. False for prod
export DJANGO_DEBUG=True

# These should run anytime the branch updates
pip --no-cache-dir install -r requirements.txt
python manage.py migrate

# Start the server (we'll want to move to using Apache mod_wsgi for prod, but for now this should be OK) (We'll need to open port 8000 on the SG)
python manage.py runserver 0.0.0.0:8000
