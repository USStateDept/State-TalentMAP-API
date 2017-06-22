#!/bin/bash

virtualenv talentmap-env
source talentmap-env/bin/activate
pip --no-cache-dir install -r requirements.txt

python manage.py runserver
