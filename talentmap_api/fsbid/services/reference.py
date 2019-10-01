import requests
import logging

from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def get_dangerpay(jwt_token):
    url = f"{API_ROOT}/dangerpays"
    danger_pay = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()
    return map(fsbid_danger_pay_to_talentmap_danger_pay, danger_pay["Data"])

def fsbid_danger_pay_to_talentmap_danger_pay(data):
    return {
        "id": data["pay_percent_num"],
        "code": data["pay_percent_num"],
        "description": data["pay_percentage_text"]
    }

def get_cycles(jwt_token):
    url = f"{API_ROOT}/cycles"
    cycles = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()
    return map(fsbid_cycles_to_talentmap_cycles, cycles["Data"])


def fsbid_cycles_to_talentmap_cycles(data):
    return {
        "id": data['cycle_id'],
        "name": data['cycle_name'],
        "active": True,
        "cycle_deadline_date": "",
        "cycle_end_date": "",
        "cycle_start_date": ""
    }


def get_bureaus(jwt_token):
    url = f"{API_ROOT}/bureaus"
    bureaus = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()
    return map(fsbid_bureaus_to_talentmap_bureaus, bureaus["Data"])


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

def get_differential_rates(jwt_token):
    # set future vacancy indicator - default to 'Y'
    url = f"{API_ROOT}/differentialrates"
    differential_rates = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()
    return map(fsbid_differential_rates_to_talentmap_differential_rates, differential_rates["Data"])

def fsbid_differential_rates_to_talentmap_differential_rates(data):
    return {
        "id": data["pay_percent_num"],
        "code": data["pay_percent_num"],
        "description": data["pay_percentage_text"]
    }

def get_grade(jwt_token):
    url = f"{API_ROOT}/grade_code"
    grade = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()
    return map(fsbid_grade_to_talentmap_grade, grade["Data"])

def fsbid_grade_to_talentmap_grade(data):
    return {
        "id": data["grade_code"],
        "code": data["grade_code"],
        "description": data["grade_code"]
    }
