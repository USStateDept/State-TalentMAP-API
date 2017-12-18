"""
WSGI config for talentmap_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from talentmap_api.common.common_helpers import load_environment_script
from django.core.wsgi import get_wsgi_application


environment = load_environment_script('../setup_environment.sh')


# https support for the swagger documentation
url_scheme = 'https'

os.environ.setdefault("DJANGO_SECRET_KEY", environment["DJANGO_SECRET_KEY"])
os.environ.setdefault("DATABASE_URL", environment["DATABASE_URL"])
os.environ.setdefault("DJANGO_DEBUG", environment["DJANGO_DEBUG"])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talentmap_api.settings")
sys.path.append(environment["DEPLOYMENT_LOCATION"])
sys.path.append(f'{environment["DEPLOYMENT_LOCATION"]}talentmap_api/')

application = get_wsgi_application()
