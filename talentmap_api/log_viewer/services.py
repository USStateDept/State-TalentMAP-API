from zipfile import ZipFile, is_zipfile

import os

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
    if os.path.exists(f"{file_name}"):
        try:
            if is_zipfile(file_name):
                with ZipFile(f"{file_name}") as myzip:
                    for f in myzip.namelist():
                        with myzip.open(f) as myfile:
                            lines = myfile.read()
            else:
                with open(f"{file_name}", 'r') as f:
                    lines = f.read()
        except FileNotFoundError:
            return None
    return {
        "data": lines
    }
