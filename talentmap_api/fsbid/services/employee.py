import logging
import jwt
import pydash

from django.conf import settings
from functools import partial
from django.contrib.auth.models import Group
from talentmap_api.fsbid.services.client import map_skill_codes, map_skill_codes_additional
from talentmap_api.fsbid.requests import requests
from talentmap_api.fsbid.services.bureau import get_bureau_positions
import talentmap_api.fsbid.services.bid as bid_services
import talentmap_api.fsbid.services.assignment_history as asg_services

from drf_yasg import openapi
from urllib.parse import urlencode, quote

API_ROOT = settings.EMPLOYEES_API_URL
ORG_ROOT = settings.ORG_API_URL
WS_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)


def get_employee_perdet_seq_num(jwt_token):
    '''
    Gets the perdet_seq_num for the employee from FSBid
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/userInfo?ad_id={ad_id}"
    employee = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    return next(iter(employee.get('Data', [])), {}).get('perdet_seq_num')


def get_employee_information(jwt_token, emp_id):
    '''
    Gets the grade and skills for the employee from FSBid
    '''
    url = f"{WS_ROOT}/v1/Persons?request_params.perdet_seq_num={emp_id}"
    skillUrl = f"{WS_ROOT}/v1/references/skills"
    employee = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    employee = next(iter(employee.get('Data', [])), {})
    employeeSkills = map_skill_codes(employee)
    skills = requests.get(skillUrl, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    skills = pydash.get(skills, 'Data', [])
    try:
        return {
            "skills": map_skill_codes(employee),
            "grade": pydash.get(employee, 'per_grade_code', '').replace(" ", ""),
            "skills_additional": map_skill_codes_additional(skills, employeeSkills),
        }
    except Exception as e:
        logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
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


def has_bureau_or_org_permissions(cp_id, jwt_token, is_bureau=True):
    get_permissions = get_bureau_permissions
    query_prop = "position__bureau__code__in"

    if not is_bureau:
        get_permissions = get_org_permissions
        query_prop = "position__org__code__in"

    permissions = list(get_permissions(jwt_token))
    codes = (','.join(pydash.map_(permissions, 'code')))

    if not codes:
        return False
    pos = get_bureau_positions(
        {
            "id": cp_id,
            query_prop: codes,
        },
        jwt_token
    )
    try:
        pos_cp_id = pydash.get(pos, 'results[0].id')
        if pos_cp_id:
            pos_cp_id = str(int(pos_cp_id))
        if pos_cp_id:
            return cp_id == pos_cp_id
    except Exception as e:
        logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        return False
    return False


def has_bureau_permissions(cp_id, jwt_token):
    return has_bureau_or_org_permissions(cp_id, jwt_token, True)


def has_org_permissions(cp_id, jwt_token):
    return has_bureau_or_org_permissions(cp_id, jwt_token, False)


def get_bureau_permissions(jwt_token, host=None):
    '''
    Gets a list of bureau codes assigned to the bureau_user
    '''
    url = f"{WS_ROOT}/v1/fsbid/bureauPermissions"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    return map(map_bureau_permissions, response.get("Data", {}))


def get_org_permissions(jwt_token, host=None):
    '''
    Gets a list of organization codes assigned to the user
    '''
    url = f"{ORG_ROOT}/Permissions"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    return map(map_org_permissions, response.get("Data", {}))

def get_separations(query, jwt_token, pk):
    '''
    Get separations
    '''
    from talentmap_api.fsbid.services.common import send_get_request
    args = {
        "uri": "v2/separations/",
        "query": query,
        "query_mapping_function": partial(convert_separations_query, pk),
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_separations,
        "count_function": None,
        "base_url": "/v2/separations/",
        "api_root": WS_ROOT,
    }

    separations = send_get_request(
        **args
    )

    return separations


def convert_separations_query(pk, query):
    '''
    Converts TalentMap query into FSBid query
    '''
    from talentmap_api.fsbid.services.common import convert_to_fsbid_ql
    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.filter": convert_to_fsbid_ql([{'col': 'sepperdetseqnum', 'val': pk}]),
        "rp.columns": 'sepperdetseqnum',
    }


    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_to_talentmap_separations(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned
    from talentmap_api.fsbid.services.common import map_return_template_cols

    hard_coded = ['seq_num', 'asgs_code', 'sepd_city', 'sepd_country_state', 'sepd_separation_date']

    add_these = ['perdet_seq_num']

    cols_mapping = {
        'seq_num': 'sepseqnum',
        'emp_seq_nbr': 'sepempseqnbr',
        'perdet_seq_num': 'sepperdetseqnum',
        'create_id': 'sepcreateid',
        'create_date': 'sepcreatedate',
        'update_id': 'sepupdateid',
        'update_date': 'sepupdatedate',
        'sepd_revision_num': 'sepdrevisionnum',
        'sepd_ail_seqnum': 'sepdailseqnum',
        'sepd_tfcd': 'sepdtfcd',
        'sepd_lat_code': 'sepdlatcode',
        'sepd_separation_date': 'sepdseparationdate',
        'sepd_dsccd': 'sepddsccd',
        'sepd_rr_repay': 'sepdwrtcoderrrepay',
        'sepd_city': 'sepdcitytext',
        'sepd_country_state': 'sepdcountrystatetext',
        'sepd_us_ind': 'sepdusind',
        'sepd_create_id': 'sepdcreateid',
        'sepd_create_date': 'sepdcreatedate',
        'sepd_update_id': 'sepdupdateid',
        'sepd_update_date': 'sepdupdatedate',
        'sepd_note_comment_text': 'sepdnotecommenttext',
        'sepd_priority_ind': 'sepdpriorityind',
        'asgs_code': 'sepdasgscode',
        'asgs_desc_text': 'asgsdesctext',
        'asgs_create_id': 'asgscreateid',
        'asgs_create_date': 'asgscreatedate',
        'asgs_update_id': 'asgsupdateid',
        'asgs_update_date': 'asgsupdatedate'
    }

    add_these.extend(hard_coded)

    return map_return_template_cols(add_these, cols_mapping, data)

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

def get_assignments_separations_bids(query, jwt_token, pk):
    asg = asg_services.assignment_history(query, jwt_token, pk)
    sep = get_separations(query, jwt_token, pk)
    sep = pydash.get(sep, 'results') if pydash.get(sep, 'results') else []
    bids = bid_services.get_bids(query, jwt_token, pk)
    bids = pydash.get(bids, 'results') if pydash.get(bids, 'results') else []

    return map(map_assignments_separations_bids, pydash.interleave(asg, sep, bids))


def map_assignments_separations_bids(data):
    return {
        "name": 'Coming Soon',
        "status": pydash.get(data, 'status') or pydash.get(data, 'asgs_code') or pydash.get(data, 'hs_code'),
        "org": pydash.get(data, 'organization') or pydash.get(data, 'TBD') or pydash.get(data, 'pos_org_short_desc'),
        "pos_num": pydash.get(data, 'position_number') or pydash.get(data, 'TBD') or pydash.get(data, 'pos_num'),
        "pos_title": pydash.get(data, 'title') or pydash.get(data, 'TBD') or pydash.get(data, 'pos_title'),
    }
