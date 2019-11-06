import requests
import logging
import os
from zipfile import ZipFile

from talentmap_api.settings import get_delineated_environment_variable
log_dir = get_delineated_environment_variable('DJANGO_LOG_DIRECTORY', '/var/log/talentmap/')


def get_log_list():
    files = []
    for file in os.listdir(log_dir):
        files.append(file)

    return {
        "data": files
    }


def get_log(log_name):
    lines = ""
    file_name = f"{log_dir}{log_name}"
    if os.path.exists(f"{file_name}.log"):
        try:
            with open(f"{file_name}.log", 'r') as f:
                lines = f.read()
        except FileNotFoundError as e:
            return None
    elif os.path.exists(f"{file_name}.zip"):
        with ZipFile(f"{file_name}.zip") as myzip:
            for f in myzip.namelist():
                with myzip.open(f) as myfile:
                    lines = myfile.read()
    return {
        "data": lines
    }
