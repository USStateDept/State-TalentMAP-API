import logging
import jwt
import pydash
import re
import maya
import csv
from datetime import datetime
from urllib.parse import urlencode, quote
from functools import partial
from copy import deepcopy

from django.utils.encoding import smart_str
from django.conf import settings
from django.http import HttpResponse

from talentmap_api.fsbid.services import common as services


API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)


def validate_agenda_item(query):
    print('🌷🌷🌷🌷🌷🌷🌷🌷🌷')
    print(query)
    print('🌷🌷🌷🌷🌷🌷🌷🌷🌷')
    validation_status = {
        'status': {
            'valid': False,
            'errorMessage': ''
        },
        'reportCategory': {
            'valid': False,
            'errorMessage': ''
        },
        'panelDate': {
            'valid': False,
            'errorMessage': ''
        },
        'remarks': {
            'valid': False,
            'errorMessage': ''
        },
        'legs': {
            'valid': False,
            'errorMessage': ''
        },
    }

    all_valid = True
    for v_s_tuple in validation_status.items():
        all_valid = all_valid and v_s_tuple[1].get('valid')
    validation_status['allValid'] = all_valid

    # AI Remarks - must not contain any inactive ones

    # print('🍭🍭🍭🍭🍭🍭🍭🍭🍭🍭')
    # print(validation_status)
    # print('🍭🍭🍭🍭🍭🍭🍭🍭🍭🍭')
    return validation_status

