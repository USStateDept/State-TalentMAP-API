import requests
import logging

from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

@staticmethod
def fsbid_danger_pay_to_talentmap_danger_pay(data):
    return {
        "id": data.get("pay_percent_num", 0),
        "code": data.get("pay_percent_num", None),
        "description": data.get("pay_percentage_text", None)
    }

@staticmethod
def fsbid_cycles_to_talentmap_cycles(data):
    return {
        "id": data.get("cycle_id", 0),
        "name": data.get("cycle_name", None),
        "active": True,
        "cycle_deadline_date": None,
        "cycle_end_date": None,
        "cycle_start_date": None
    }

@staticmethod
def fsbid_bureaus_to_talentmap_bureaus(data):
    return {
        "bureau_organization": None,
        "code": data.get("bur", None),
        "groups": [],
        "highlighted_positions": [],
        "id": data.get("bur", 0),
        "is_bureau": True,
        "is_regional": True if data.get("isregional", None) == 0 else False,
        "location": None,
        "long_description": data.get("bureau_long_desc", None),
        "parent_organization": None,
        "short_description": data.get("bureau_short_desc", None)
    }

@staticmethod
def fsbid_differential_rates_to_talentmap_differential_rates(data):
    return {
        "id": data.get("pay_percent_num", 0),
        "code": data.get("pay_percent_num", None),
        "description": data.get("pay_percentage_text", None)
    }

@staticmethod
def fsbid_grade_to_talentmap_grade(data):
    return {
        "id": data.get("grade_code", 0),
        "code": data.get("grade_code", None),
        "description": None
    }

@staticmethod
def fsbid_languages_to_talentmap_languages(data):
    return {
        "id": data.get("language_code", 0),
        "code": data.get("language_code", None),
        "formal_description": data.get("language_long_desc", None),
        "long_description": data.get("language_long_desc", None),
        "short_description": data.get("language_short_desc", None),
        "effective_date": None
    }

@staticmethod
def fsbid_tour_of_duties_to_talentmap_tour_of_duties(data):
    return {
        "id": data.get("code", 0),
        "code": data.get("code", 0),
        "is_active": True,
        "months": None,
        "long_description": data.get("long_desc", None),
        "short_description": data.get("long_desc", None)
    }
