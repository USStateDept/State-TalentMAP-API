import requests
import logging
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
    try:
        with open(log_dir + '/' + log_name + ".log", 'r') as f:
            lines = f.read()
    except FileNotFoundError as e:
        return None

    return {
        "data": lines
    }
