"""
WSGI config for talentmap_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from talentmap_api.common.common_helpers import load_environment_script
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# https support for the swagger documentation
url_scheme = 'https'

# Don't load from setup environment file if we're running development server
if 'runserver' not in sys.argv:
    environment = load_environment_script(os.path.join(settings.BASE_DIR, 'setup_environment.sh'))

    for environment_variable in environment.keys():
        os.environ.setdefault(environment_variable, environment[environment_variable])

    sys.path.append(environment["DEPLOYMENT_LOCATION"])
    sys.path.append(f'{environment["DEPLOYMENT_LOCATION"]}talentmap_api/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talentmap_api.settings")

application = get_wsgi_application()
