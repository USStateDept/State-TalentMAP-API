import requests
import logging

from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def fsbid_danger_pay_to_talentmap_danger_pay(data):
    return {
        "id": data["pay_percent_num"],
        "code": data["pay_percent_num"],
        "description": data["pay_percentage_text"]
    }

def fsbid_cycles_to_talentmap_cycles(data):
    return {
        "id": data['cycle_id'],
        "name": data['cycle_name'],
        "active": True,
        "cycle_deadline_date": "",
        "cycle_end_date": "",
        "cycle_start_date": ""
    }

def fsbid_bureaus_to_talentmap_bureaus(data):
    return {
        "bureau_organization": "",
        "code": data['bur'],
        "groups": [],
        "highlighted_positions": [],
        "id": data['bur'],
        "is_bureau": True,
        "is_regional": True if data['isregional'] == 0 else False,
        "location": "",
        "long_description": data['bureau_long_desc'],
        "parent_organization": "",
        "short_description": data['bureau_short_desc']
    }

def fsbid_differential_rates_to_talentmap_differential_rates(data):
    return {
        "id": data["pay_percent_num"],
        "code": data["pay_percent_num"],
        "description": data["pay_percentage_text"]
    }

def fsbid_grade_to_talentmap_grade(data):
    return {
        "id": data["grade_code"],
        "code": data["grade_code"],
        "description": data["grade_code"]
    }

def fsbid_languages_to_talentmap_languages(data):
    return {
        "id": data["language_code"],
        "code": data["language_code"],
        "formal_description": data["language_long_desc"],
        "long_description": data["language_long_desc"],
        "short_description": data["language_short_desc"],
        "effective_date": ""
    }

def fsbid_tour_of_duties_to_talentmap_tour_of_duties(data):
    return {
        "id": data["code"],
        "code": data["code"],
        "is_active": True,
        "months": "",
        "long_description": data["long_desc"],
        "short_description": data["long_desc"]
    }
