"""
WSGI config for talentmap_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
import re

from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_environment_script(file):
    '''
    Attempts to load environment data from the specified location

    Args:
        - file (String) - The path to the file

    Return:
        - dictionary (Object) - A dictionary of variable-key pairs
    '''

    environment_file = {}
    try:
        with open(file) as f:
            for variable in re.finditer(r'export (.*?)=(.+)', f.read()):
                # print(f"Found setup_environment.sh variable: {variable.group(1)}={variable.group(2)}")
                # Store the variable, and strip any extra apostrophes or quotation marks
                environment_file[variable.group(1)] = variable.group(2).replace("\'", "").replace("\"", "")
    except:
        print(f'TalentMAP: wsgi.py unable to load environment, does {file} exist?')
        raise

    return environment_file


# https support for the swagger documentation
url_scheme = 'https'

# Don't load from setup environment file if we're running development server
if 'runserver' not in sys.argv:
    environment = load_environment_script(os.path.join(BASE_DIR, 'setup_environment.sh'))

    env_name = ''
    if "DJANGO_ENVIRONMENT_NAME" in environment:
        print(f'Setting DJANGO_ENVIRONMENT_NAME to {environment["DJANGO_ENVIRONMENT_NAME"]}')
        env_name = environment["DJANGO_ENVIRONMENT_NAME"]

    # Explicitly set the environment name here to ensure our helper method can locate it
    os.environ.setdefault("DJANGO_ENVIRONMENT_NAME", env_name)

    for environment_variable in environment.keys():
        os.environ.setdefault(f"{env_name}{environment_variable}", environment[environment_variable])

    sys.path.append(environment["DEPLOYMENT_LOCATION"])
    sys.path.append(f'{environment["DEPLOYMENT_LOCATION"]}talentmap_api/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talentmap_api.settings")

application = get_wsgi_application()
