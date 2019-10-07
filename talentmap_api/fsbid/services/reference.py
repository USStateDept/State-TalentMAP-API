import requests
import logging

from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def fsbid_danger_pay_to_talentmap_danger_pay(data):
    return {
        "id": data.get("pay_percent_num", ""),
        "code": data.get("pay_percent_num", ""),
        "description": data.get("pay_percentage_text", "")
    }

def fsbid_cycles_to_talentmap_cycles(data):
    return {
        "id": data.get("cycle_id", ""),
        "name": data.get("cycle_name", ""),
        "active": True,
        "cycle_deadline_date": "",
        "cycle_end_date": "",
        "cycle_start_date": ""
    }

def fsbid_bureaus_to_talentmap_bureaus(data):
    return {
        "bureau_organization": "",
        "code": data.get("bur", ""),
        "groups": [],
        "highlighted_positions": [],
        "id": data.get("bur", ""),
        "is_bureau": True,
        "is_regional": True if data.get("isregional", "") == 0 else False,
        "location": "",
        "long_description": data.get("bureau_long_desc", ""),
        "parent_organization": "",
        "short_description": data.get("bureau_short_desc", "")
    }

def fsbid_differential_rates_to_talentmap_differential_rates(data):
    return {
        "id": data.get("pay_percent_num", ""),
        "code": data.get("pay_percent_num", ""),
        "description": data.get("pay_percentage_text", "")
    }

def fsbid_grade_to_talentmap_grade(data):
    return {
        "id": data.get("grade_code", ""),
        "code": data.get("grade_code", ""),
        "description": ""
    }

def fsbid_languages_to_talentmap_languages(data):
    return {
        "id": data.get("language_code", ""),
        "code": data.get("language_code", ""),
        "formal_description": data.get("language_long_desc", ""),
        "long_description": data.get("language_long_desc", ""),
        "short_description": data.get("language_short_desc", ""),
        "effective_date": ""
    }

def fsbid_tour_of_duties_to_talentmap_tour_of_duties(data):
    return {
        "id": data.get("code", 0),
        "code": data.get("code", 0),
        "is_active": True,
        "months": "",
        "long_description": data.get("long_desc", ""),
        "short_description": data.get("long_desc", "")
    }
