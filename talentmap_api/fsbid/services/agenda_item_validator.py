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
    validation_status = {
        'status': validate_status(query['agendaStatusCode']),
        'reportCategory': validate_report_category(query['panelMeetingCategory']),
        'panelDate': validate_panel_date(query['panelMeetingId']),
        'legs': validate_legs(query['agendaLegs']),
    }

    all_valid = True
    for v_s_tuple in validation_status.items():
        all_valid = all_valid and v_s_tuple[1].get('valid')
    validation_status['allValid'] = all_valid

    return validation_status

def validate_status(status):
    status_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # AI Status - must make selection
    if not status:
        status_validation['valid'] = False
        status_validation['errorMessage'] = 'No Status Selected'

    return status_validation

def validate_report_category(category):
    category_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # AI Category - must make selection
    if not category:
        category_validation['valid'] = False
        category_validation['errorMessage'] = 'No Category Selected'

    return category_validation

def validate_panel_date(date):
    date_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # AI Date - must make selection
    if not date:
        date_validation['valid'] = False
        date_validation['errorMessage'] = 'No Panel Date Selected'

    return date_validation

def validate_legs(legs):
    legs_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # AI Legs - must not be empty
    if not len(legs):
        legs_validation['valid'] = False
        legs_validation['errorMessage'] = 'Agenda Items must have at least one leg.'

    return legs_validation
