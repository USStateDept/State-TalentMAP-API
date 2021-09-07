import logging
import requests
import jwt
import pydash

from django.conf import settings
from django.contrib.auth.models import Group
from talentmap_api.fsbid.services.client import map_skill_codes, map_skill_codes_additional
from talentmap_api.fsbid.services.available_positions import get_available_position
from talentmap_api.fsbid.services.bureau import get_bureau_positions

API_ROOT = settings.EMPLOYEES_API_URL
FSBID_ROOT = settings.FSBID_API_URL
ORG_ROOT = settings.ORG_API_URL

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
    skillUrl = f"{FSBID_ROOT}/skillCodes"
    employee = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    employee = next(iter(employee.get('Data', [])), {})
    employeeSkills = map_skill_codes(employee)
    skills = requests.get(skillUrl, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    skills = pydash.get(skills, 'Data', [])
    try:
        return {
            "skills": map_skill_codes(employee),
            "grade": pydash.get(employee, 'per_grade_code', '').replace(" ", ""),
            "skills_additional": map_skill_codes_additional(skills, employeeSkills),
        }
    except:
        return {}


def map_group_to_fsbid_role(jwt_token):
    '''
    Updates a user roles based on what we get back from FSBid
    '''
    roles = jwt.decode(jwt_token, verify=False).get('role')
    if isinstance(roles, str):
        roles = [roles]
    tm_roles = list(map(lambda z: ROLE_MAPPING.get(z), roles))

    orgPermissions = list(get_org_permissions(jwt_token))
    if len(orgPermissions) >= 1:
        tm_roles.append('post_user')
    
    # For developer testing
    if 'developer' in roles:
        developerRoles = ['fsofficer', 'CDO', 'Bureau', 'AO']
        mappedDeveloperRoles = list(map(lambda z: ROLE_MAPPING.get(z), developerRoles))
        tm_roles += mappedDeveloperRoles
        tm_roles = pydash.uniq(tm_roles)

    return Group.objects.filter(name__in=tm_roles).all()


# Mapping of FSBid roles (keys) to TalentMap permissions (values)
ROLE_MAPPING = {
    # post_user gets manually mapped, but we still include it here so it can be removed if necessary
    "post_user": "post_user",
    "fsofficer": "bidder",
    "FSBidCycleAdministrator": "bidcycle_admin",
    "CDO": "cdo",
    "CDO3": "cdo",
    "Bureau": "bureau_user",
    "AO": "ao_user",
}

def has_bureau_permissions(cp_id, jwt_token):
    bureauPermissions = list(get_bureau_permissions(jwt_token))
    bureauCodes = (','.join(pydash.map_(bureauPermissions, 'code')))
    pos = get_bureau_positions(
        {
            "id": cp_id,
            "position__bureau__code__in": bureauCodes,
        },
        jwt_token
    )
    try:
        bureau = str(pos['results'][0].get('position').get('bureau_code'))
        return any(x.get('code') == bureau for x in bureauPermissions)
    except:
        return False
    return False

def has_org_permissions(cp_id, jwt_token):
    pos = get_available_position(cp_id, jwt_token)
    orgPermissions = list(get_org_permissions(jwt_token))
    try:
        org = str(pos.get('position').get('organization_code'))
        return any(x.get('code') == org for x in orgPermissions)
    except:
        return False
    return False

def get_bureau_permissions(jwt_token, host=None):
    '''
    Gets a list of bureau codes assigned to the bureau_user
    '''
    url = f"{FSBID_ROOT}/bureauPermissions"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return map(map_bureau_permissions, response.get("Data", {}))

def get_org_permissions(jwt_token, host=None):
    '''
    Gets a list of organization codes assigned to the user
    '''
    url = f"{ORG_ROOT}/Permissions"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return map(map_org_permissions, response.get("Data", {}))

def map_bureau_permissions(data):
    return {
        "code": data.get('bur', None),
        "long_description": data.get('bureau_long_desc', None),
        "short_description": data.get('bureau_short_desc', None),
    }

def map_org_permissions(data):
    return {
        "code": data.get('org_code', None),
        "long_description": data.get('org_long_desc', None),
        "short_description": data.get('org_short_desc', None),
    }
