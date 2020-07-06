import logging
import requests
import jwt

from django.conf import settings
from django.contrib.auth.models import Group
from talentmap_api.fsbid.services.client import map_skill_codes

API_ROOT = settings.EMPLOYEES_API_URL
FSBID_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)


def get_employee_perdet_seq_num(jwt_token):
    '''
    Gets the perdet_seq_num for the employee from FSBid
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/userInfo?ad_id={ad_id}"
    employee = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return next(iter(employee.get('Data', [])), {}).get('perdet_seq_num')


def get_employee_information(jwt_token, emp_id):
    '''
    Gets the grade and skills for the employee from FSBid
    '''
    url = f"{FSBID_ROOT}/Persons?request_params.perdet_seq_num={emp_id}"
    employee = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    employee = next(iter(employee.get('Data', [])), {})
    try:
        return {
            "skills": map_skill_codes(employee),
            "grade": employee['per_grade_code'].replace(" ", "")
        }
    except:
        return {}


def map_group_to_fsbid_role(jwt_token):
    '''
    Updates a user roles based on what we get back from FSBid
    '''
    roles = jwt.decode(jwt_token, verify=False).get('role')
    print(roles)
    tm_roles = list(map(lambda z: ROLE_MAPPING.get(z), roles))
    print(tm_roles)
    return Group.objects.filter(name__in=tm_roles).all()


# Mapping of FSBid roles (keys) to TalentMap permissions (values)
ROLE_MAPPING = {
    "fsofficer": "bidder",
    "FSBidCycleAdministrator": "bidcycle_admin",
    "CDO": "cdo",
    "CDO3": "cdo",
}
