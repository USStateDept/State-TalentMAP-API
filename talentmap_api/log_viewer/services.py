from zipfile import ZipFile, is_zipfile

import subprocess
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


def get_log(log_name, size=1000):
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
                lines = tail(file_name, size)
        except FileNotFoundError:
            return None
    return {
        "data": lines
    }


def tail(f, n):
    print(f)
    proc = subprocess.Popen(['tail', '-n', str(n), f], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    lines = ''.join(bytes.join(b'', lines).decode('ascii'))
    return lines
