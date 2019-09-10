#! /bin/bash

# "Automation" of the API app deployment.
# * Sets up virtual env
# * Gets code from the `dev` branch
# * sets up environment vars
# * install dependencies
# * run migrations
# * restart server

# Create and activate virtual env
virtualenv --python=/usr/bin/python3 venv
source venv/bin/activate

curr_date=`date "+%Y-%m-%d_%H-%M-%S"`

# backup current version if it exists
[ -d State-TalentMAP-API-dev ] && mv State-TalentMAP-API-dev State-TalentMAP-API-dev-$curr_date

# get code
wget -O dev.zip https://github.com/MetaPhase-Consulting/State-TalentMAP-API/archive/dev.zip

unzip -o dev.zip
rm dev.zip
cd State-TalentMAP-API-dev

# copy env setup script
cp EXAMPLE_setup_environment.sh setup_environment.sh
# setup env
source setup_environment.sh

export DATABASE_URL='<DATABASE_URL>'
export DJANGO_LOG_DIRECTORY='/home/ec2-user/log/'
export DEPLOYMENT_LOCATION='/home/ec2-user/State-TalentMAP-API-dev/'
export FSBID_API_URL='https://mockfsbid.metaphasedev.com'

# install dependencies
pip install -r requirements.txt

python manage.py migrate

# Stop the server
pkill -f runserver

python manage.py runserver 0.0.0.0:8000 &>/dev/null &

echo "Deployment complete"

exit