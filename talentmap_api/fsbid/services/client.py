import csv
import logging
from copy import deepcopy
from datetime import datetime
from urllib.parse import urlencode, quote
from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import smart_str
import jwt
import pydash

import requests  # pylint: disable=unused-import

import talentmap_api.fsbid.services.cdo as cdo_services
import talentmap_api.fsbid.services.available_positions as services_ap
from talentmap_api.common.common_helpers import ensure_date

API_ROOT = settings.FSBID_API_URL
HRDATA_URL = settings.HRDATA_URL
HRDATA_URL_EXTERNAL = settings.HRDATA_URL_EXTERNAL
SECREF_ROOT = settings.SECREF_URL
CLIENTS_ROOT = settings.CLIENTS_API_URL

logger = logging.getLogger(__name__)


def get_user_information(jwt_token, perdet_seq_num):
    '''
    Gets the office_phone and office_address for the employee
    '''
    url = f"{SECREF_ROOT}/user?request_params.perdet_seq_num={perdet_seq_num}"
    user = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'},
                            verify=False).json()  # nosec
    user = next(iter(user.get('Data', [])), {})
    try:
        return {
            "office_address": user['gal_address_text'],
            "office_phone": user['gal_phone_nbr_text'],
            "email": user['gal_smtp_email_address_text'],
        }
    except:
        return {}


def client(jwt_token, query, host=None):
    '''
    Get Clients by CDO
    '''
    from talentmap_api.fsbid.services.common import send_get_request
    uri = "CDOClients"
    response = send_get_request(
        uri,
        query,
        convert_client_query,
        jwt_token,
        fsbid_clients_to_talentmap_clients,
        get_clients_count,
        "/api/v1/fsbid/CDOClients/",
        host
    )

    return response


def get_clients_count(query, jwt_token, host=None):
    '''
    Gets the total number of available positions for a filterset
    '''
    from talentmap_api.fsbid.services.common import send_count_request
    return send_count_request("CDOClients", query, convert_client_count_query, jwt_token, host)


def client_suggestions(jwt_token, perdet_seq_num):
    '''
    Get a suggestion for a client
    '''

    # if less than LOW, try broader query
    LOW = 5
    # but also don't go too high
    HIGH = 100
    # but going over HIGH is preferred over FLOOR
    FLOOR = 0

    CLIENT = single_client(jwt_token, perdet_seq_num)
    grade = CLIENT.get("grade")
    skills = CLIENT.get("skills")
    skills = deepcopy(skills)
    mappedSkills = ','.join([str(x.get("code")) for x in skills])

    values = {
        "position__grade__code__in": grade,
        "position__skill__code__in": mappedSkills,
    }

    # Dictionary for the next grade "up"
    nextGrades = {
        "08": "07",
        "07": "06",
        "06": "05",
        "05": "04",
        "04": "03",
        "02": "01",
    }

    count = services_ap.get_available_positions_count(values, jwt_token)
    count = int(count.get("count"))

    # If we get too few results, try a broader query
    if count < LOW and nextGrades.get(grade) is not None:
        nextGrade = nextGrades.get(grade)
        values2 = deepcopy(values)
        values2["position__grade__code__in"] = f"{grade},{nextGrade}"
        count2 = services_ap.get_available_positions_count(values2, jwt_token)
        count2 = int(count2.get("count"))
        # Only use our broader query if the first one <= FLOOR OR the second < HIGH, and the counts don't match
        if (count <= FLOOR or count2 < HIGH) and count != count2:
            values = values2

    # Finally, return the query
    return values


def single_client(jwt_token, perdet_seq_num):
    '''
    Get a single client for a CDO
    '''
    from talentmap_api.fsbid.services.common import get_fsbid_results
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"CDOClients?request_params.ad_id={ad_id}&request_params.perdet_seq_num={perdet_seq_num}&request_params.currentAssignmentOnly=false"
    uriCurrentAssignment = f"CDOClients?request_params.ad_id={ad_id}&request_params.perdet_seq_num={perdet_seq_num}&request_params.currentAssignmentOnly=true"
    response = get_fsbid_results(uri, jwt_token, fsbid_clients_to_talentmap_clients)
    responseCurrentAssignment = get_fsbid_results(uriCurrentAssignment, jwt_token, fsbid_clients_to_talentmap_clients)
    cdo = cdo_services.single_cdo(jwt_token, perdet_seq_num)
    user_info = get_user_information(jwt_token, perdet_seq_num)
    CLIENT = list(response)[0]
    CLIENT['cdo'] = cdo
    CLIENT['user_info'] = user_info
    CLIENT['current_assignment'] = list(responseCurrentAssignment)[0].get('current_assignment', {})
    return CLIENT


def get_client_csv(query, jwt_token, rl_cd, host=None):
    from talentmap_api.fsbid.services.common import send_get_csv_request
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    data = send_get_csv_request(
        "CDOClients",
        query,
        convert_client_query,
        jwt_token,
        fsbid_clients_to_talentmap_clients_for_csv,
        API_ROOT,
        host,
        ad_id
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=clients_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Email"),
        smart_str(u"Skill"),
        smart_str(u"Grade"),
        smart_str(u"Employee ID"),
        # smart_str(u"Role Code"), Might not be useful to users
        smart_str(u"Position Location Code"),
    ])

    for record in data:
        email_response = get_user_information(jwt_token, record['id'])
        email = pydash.get(email_response, 'email') or 'None listed' 
        writer.writerow([
            smart_str(record["name"]),
            email,
            smart_str(record["skills"]),
            smart_str("=\"%s\"" % record["grade"]),
            smart_str("=\"%s\"" % record["employee_id"]),
            # smart_str(record["role_code"]), Might not be useful to users
            smart_str("=\"%s\"" % record["pos_location"]),
        ])
    return response


def fsbid_clients_to_talentmap_clients(data):
    from talentmap_api.fsbid.services.common import get_employee_profile_urls
    employee = data.get('employee', None)
    current_assignment = None
    assignments = None
    position = None
    location = {}

    if employee is not None:
        current_assignment = employee.get('currentAssignment', None)

    if employee.get('assignment', None) is not None:
        assignments = employee.get('assignment', None)
        # handle if array
        if type(assignments) is type([]) and list(assignments):
            current_assignment = list(assignments)[0]
        # handle if object
        if type(assignments) is type(dict()):
            current_assignment = assignments
            # remove current prefix
            if assignments.get('currentPosition', None) is not None:
                assignments['position'] = assignments['currentPosition']
                assignments['position']['location'] = assignments['currentPosition']['currentLocation']
                assignments = [].append(assignments)

    if current_assignment is not None:
        # handle if object
        if current_assignment.get('currentPosition', None) is not None:
            position = current_assignment.get('currentPosition', None)
        # handle if array
        if current_assignment.get('position', None) is not None:
            position = current_assignment.get('position', None)

    if position is not None:
        # handle if object
        if position.get('currentLocation', None) is not None:
            location = position.get('currentLocation', {})
        # handle if array
        if position.get('location', None) is not None:
            location = position.get('location', {})

    if current_assignment and current_assignment.get('currentPosition', None) is not None:
        # remove current prefix
        current_assignment['position'] = current_assignment['currentPosition']
        current_assignment['position']['location'] = current_assignment['position']['currentLocation']

    # first object in array, mapped
    try:
        current_assignment = fsbid_assignments_to_tmap(current_assignment)[0]
    except:
        current_assignment = {}

    initials = None
    try:
        initials = employee['per_first_name'][:1] + employee['per_last_name'][:1]
    except:
        initials = None

    middle_name = get_middle_name(employee)

    return {
        "id": str(employee.get("pert_external_id", None)),
        "name": f"{employee.get('per_first_name', None)} {middle_name['full']}{employee.get('per_last_name', None)}",
        "shortened_name": f"{employee.get('per_last_name', None)}, {employee.get('per_first_name', None)} {middle_name['initial']}",
        "initials": initials,
        "perdet_seq_number": str(employee.get("perdet_seq_num", None)),
        "grade": employee.get("per_grade_code", None),
        "skills": map_skill_codes(employee),
        "employee_id": str(employee.get("pert_external_id", None)),
        "role_code": data.get("rl_cd", None),
        "pos_location": map_location(location),
        # not exposed in FSBid yet
        # "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd")),
        # "noPanel": fsbid_no_successful_panel_to_tmap(data.get("no_successful_panel")),
        # "noBids": fsbid_no_bids_to_tmap(data.get("no_bids")),
        "classifications": fsbid_classifications_to_tmap(employee.get("classifications", [])),
        "current_assignment": current_assignment,
        "assignments": fsbid_assignments_to_tmap(assignments),
        "employee_profile_url": get_employee_profile_urls(employee.get("perdet_seq_num", None)),
    }


def fsbid_clients_to_talentmap_clients_for_csv(data):
    employee = data.get('employee', None)
    current_assignment = employee.get('currentAssignment', None)
    pos_location = None
    middle_name = get_middle_name(employee)
    if current_assignment is not None:
        position = current_assignment.get('currentPosition', None)
        if position is not None:
            pos_location = map_location(position.get("currentLocation", None))

    return {
        "id": employee.get("perdet_seq_num", None),
        "name": f"{employee.get('per_first_name', None)} {middle_name['full']}{employee.get('per_last_name', None)}",
        "grade": employee.get("per_grade_code", None),
        "skills": ' , '.join(map_skill_codes_for_csv(employee)),
        "employee_id": employee.get("pert_external_id", None),
        "role_code": data.get("rl_cd", None),
        "pos_location": pos_location,
        # not exposed in FSBid yet
        # "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd")),
        # "noPanel": fsbid_no_successful_panel_to_tmap(data.get("no_successful_panel")),
        # "noBids": fsbid_no_bids_to_tmap(data.get("no_bids")),
        "classifications": fsbid_classifications_to_tmap(employee.get("classifications", []))
    }


def get_middle_name(employee):
    middle_name = employee.get('per_middle_name', None) or ''
    middle_initial = ''
    if middle_name == 'NMN':
        middle_name = ''
    if middle_name:
        middle_name = middle_name + ' '
        middle_initial = middle_name[:1] + ' '
    return {"full": middle_name, "initial": middle_initial}


def hru_id_filter(query):
    from talentmap_api.fsbid.services.common import convert_multi_value
    results = []
    hru_id = query.get("hru_id", None)
    results += [hru_id] if hru_id is not None else []
    hru_ids = convert_multi_value(query.get("hru_id__in", None))
    results += hru_ids if hru_ids is not None else []
    return results if len(results) > 0 else None


def convert_client_query(query, isCount=None):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the client search filter naming
    '''
    from talentmap_api.fsbid.services.common import sorting_values, convert_multi_value
    values = {
        "request_params.hru_id": hru_id_filter(query),
        "request_params.rl_cd": query.get("rl_cd", None),
        "request_params.ad_id": query.get("ad_id", None),
        "request_params.order_by": sorting_values(query.get("ordering", None)),
        "request_params.freeText": query.get("q", None),
        "request_params.bsn_id": convert_multi_value(query.get("bid_seasons")),
        "request_params.hs_cd": tmap_handshake_to_fsbid(query.get('hasHandshake', None)),
        "request_params.no_successful_panel": tmap_no_successful_panel_to_fsbid(query.get('noPanel', None)),
        "request_params.no_bids": tmap_no_bids_to_fsbid(query.get('noBids', None)),
        "request_params.page_index": int(query.get("page", 1)),
        "request_params.page_size": query.get("limit", 25),
        "request_params.currentAssignmentOnly": query.get("currentAssignmentOnly", 'true'),
        "request_params.get_count": query.get("getCount", 'false'),
    }
    if isCount:
        values['request_params.page_size'] = None
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)


def convert_client_count_query(query):
    return convert_client_query(query, True)


def map_skill_codes_for_csv(data, prefix='per'):
    skills = []
    for i in range(1, 4):
        index = f'_{i}'
        if i == 1:
            index = ''
        desc = data.get(f'{prefix}_skill{index}_code_desc', None)
        skills.append(desc)
    return filter(lambda x: x is not None, skills)


def map_skill_codes(data):
    skills = []
    for i in range(1, 4):
        index = f'_{i}'
        if i == 1:
            index = ''
        code = pydash.get(data, f'per_skill{index}_code', None)
        desc = pydash.get(data, f'per_skill{index}_code_desc', None)
        skills.append({'code': code, 'description': desc})
    return filter(lambda x: x.get('code', None) is not None, skills)


def map_skill_codes_additional(skills, employeeSkills):
    employeeCodesAdd = []
    for w in employeeSkills:
        foundSkill = [a for a in skills if a['skl_code'] == w['code']][0]
        cone = foundSkill['jc_nm_txt']
        foundSkillsByCone = [b for b in skills if b['jc_nm_txt'] == cone]
        for x in foundSkillsByCone:
            employeeCodesAdd.append(x['skl_code'])
    return set(employeeCodesAdd)


def map_location(location):
    city = location.get('city')
    country = location.get('country')
    state = location.get('state')
    result = city
    if country and country.strip():
        result = f"{city}, {country}"
    if state and state.strip():
        result = f"{city}, {state}"
    return result


def fsbid_handshake_to_tmap(hs):
    # Maps FSBid Y/N value for handshakes to expected TMap Front end response for handshake
    fsbid_dictionary = {
        "Y": True,
        "N": False
    }
    return fsbid_dictionary.get(hs, None)


def tmap_handshake_to_fsbid(hs):
    # Maps TMap true/false value to acceptable fsbid api params for handshake
    tmap_dictionary = {
        "true": "Y",
        "false": "N"
    }
    return tmap_dictionary.get(hs, None)

def fsbid_no_successful_panel_to_tmap(panel):
    fsbid_dictionary = {
        "Y": True,
        "N": False
    }
    return fsbid_dictionary.get(panel, None)


def tmap_no_successful_panel_to_fsbid(panel):
    tmap_dictionary = {
        "true": "Y",
        "false": "N"
    }
    return tmap_dictionary.get(panel, None)

def fsbid_no_bids_to_tmap(bids):
    fsbid_dictionary = {
        "Y": True,
        "N": False
    }
    return fsbid_dictionary.get(bids, None)


def tmap_no_bids_to_fsbid(bids):
    tmap_dictionary = {
        "true": "Y",
        "false": "N"
    }
    return tmap_dictionary.get(bids, None)


def fsbid_classifications_to_tmap(cs):
    tmap_classifications = []
    if type(cs) is list:
        for x in cs:
            tmap_classifications.append(
                # resolves disrepancy between string and number comparison
                pydash.to_number(x.get('te_id', None))
            )
    else:
        tmap_classifications.append(
            # resolves disrepancy between string and number comparison
            pydash.to_number(cs.get('te_id', None))
        )
    return tmap_classifications


def fsbid_assignments_to_tmap(assignments):
    from talentmap_api.fsbid.services.common import get_post_overview_url, get_post_bidding_considerations_url, get_obc_id
    assignmentsCopy = []
    tmap_assignments = []
    if type(assignments) is type(dict()):
        assignmentsCopy.append(assignments)
    else:
        assignmentsCopy = assignments
    if type(assignmentsCopy) is type([]):
        for x in assignmentsCopy:
            pos = x.get('position', {})
            loc = pos.get('location', {})
            tmap_assignments.append(
                {
                    "id": x.get('asg_seq_num', None),
                    "position_id": x.get('pos_seq_num', None),
                    "start_date": ensure_date(x.get('asgd_eta_date', None)),
                    "end_date": ensure_date(x.get('asgd_etd_ted_date', None)),
                    "position": {
                        "grade": pos.get("pos_grade_code", None),
                        "skill": f"{pos.get('pos_skill_desc', None)} ({pos.get('pos_skill_code')})",
                        "skill_code": pos.get("pos_skill_code", None),
                        "bureau": f"({pos.get('pos_bureau_short_desc', None)}) {pos.get('pos_bureau_long_desc', None)}",
                        "bureau_code": pydash.get(pos, 'bureau.bureau_short_desc'), # only comes through for available bidders
                        "organization": pos.get('pos_org_short_desc', None),
                        "position_number": pos.get('pos_seq_num', None),
                        "title": pos.get("pos_title_desc", None),
                        "post": {
                            "code": loc.get("gvt_geoloc_cd", None),
                            "post_overview_url": get_post_overview_url(loc.get("gvt_geoloc_cd", None)),
                            "post_bidding_considerations_url": get_post_bidding_considerations_url(loc.get("gvt_geoloc_cd", None)),
                            "obc_id": get_obc_id(loc.get("gvt_geoloc_cd", None)),
                            "location": {
                                "country": loc.get("country", None),
                                "code": loc.get("gvt_geoloc_cd", None),
                                "city": loc.get("city", None),
                                "state": loc.get("state", None),
                            }
                        },
                        "language": pos.get("pos_position_lang_prof_desc", None)
                    },
                }
            )
    return tmap_assignments


def fsbid_languages_to_tmap(languages):
    tmap_languages = []
    for x in languages:
        tmap_languages.append({
            "code": x.get('empl_language_code', None),
            "language": x.get('empl_language', None),
            "test_date": ensure_date(x.get('empl_high_test_date', None)),
            "speaking_score": x.get('empl_high_speaking', None),
            "reading_score": x.get('empl_high_reading', None),
            "custom_description": f"{x.get('empl_language')} {x.get('empl_high_speaking')}/{x.get('empl_high_reading')}"
        })
    return tmap_languages


def get_available_bidders(jwt_token, isCDO, query, host=None):
    from talentmap_api.fsbid.services.common import send_get_request
    from talentmap_api.cdo.services.available_bidders import get_available_bidders_stats
    cdo = 'cdo' if isCDO else 'bureau'
    uri = f"availablebidders/{cdo}"
    response = send_get_request(
        uri,
        query,
        convert_available_bidder_query,
        jwt_token,
        fsbid_available_bidder_to_talentmap,
        False, # No count function
        f"/api/v1/clients/availablebidders/{cdo}",
        host,
        CLIENTS_ROOT,
    )
    stats = get_available_bidders_stats()
    return {
        **stats,
        "results": list({v['perdet_seq_number']:v for v in response.get('results')}.values()),
    }

# Can update to reuse client mapping once client v2 is updated and released with all the new fields
def fsbid_available_bidder_to_talentmap(data):
    from talentmap_api.fsbid.services.common import get_employee_profile_urls
    employee = data.get('employee', None)
    current_assignment = None
    assignments = None
    position = None
    location = {}

    if employee is not None:
        current_assignment = employee.get('currentAssignment', None)

    if employee.get('assignment', None) is not None:
        assignments = employee.get('assignment', None)
        # handle if array
        if type(assignments) is type([]) and list(assignments):
            current_assignment = list(assignments)[0]
        # handle if object
        if type(assignments) is type(dict()):
            current_assignment = assignments
            # remove current prefix
            if assignments.get('currentPosition', None) is not None:
                assignments['position'] = assignments['currentPosition']
                assignments['position']['location'] = assignments['currentPosition']['currentLocation']
                assignments = [].append(assignments)

    if current_assignment is not None:
        # handle if object
        if current_assignment.get('currentPosition', None) is not None:
            position = current_assignment.get('currentPosition', None)
        # handle if array
        if current_assignment.get('position', None) is not None:
            position = current_assignment.get('position', None)

    if position is not None:
        # handle if object
        if position.get('currentLocation', None) is not None:
            location = position.get('currentLocation', {})
        # handle if array
        if position.get('location', None) is not None:
            location = position.get('location', {})

    if current_assignment and current_assignment.get('currentPosition', None) is not None:
        # remove current prefix
        current_assignment['position'] = current_assignment['currentPosition']
        current_assignment['position']['location'] = current_assignment['position']['currentLocation']

    # first object in array, mapped
    try:
        current_assignment = fsbid_assignments_to_tmap(current_assignment)[0]
    except:
        current_assignment = {}

    initials = None
    try:
        initials = employee['per_first_name'][:1] + employee['per_last_name'][:1]
    except:
        initials = None

    middle_name = get_middle_name(employee)

    res = {
        "id": str(employee.get("pert_external_id", None)),
        "cdo": {
            "full_name": data.get('cdo_fullname', None),
            "last_name": data.get('cdo_last_name', None),
            "first_name": data.get('cdo_first_name', None),
            "email": data.get('cdo_email', None),
            "hru_id": data.get("hru_id", None),
        },
        "name": f"{employee.get('per_last_name', None)}, {employee.get('per_first_name', None)} {middle_name['initial']}",
        "shortened_name": f"{employee.get('per_first_name', None)} {middle_name['initial']}{employee.get('per_last_name', None)}",
        "initials": initials,
        "perdet_seq_number": str(employee.get("perdet_seq_num", None)),
        "grade": employee.get("per_grade_code", None),
        "skills": map_skill_codes(employee),
        "employee_id": str(employee.get("pert_external_id", None)),
        "role_code": data.get("rl_cd", None),
        "pos_location": map_location(location),
        # not exposed in FSBid yet
        # "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd")),
        # "noPanel": fsbid_no_successful_panel_to_tmap(data.get("no_successful_panel")),
        # "noBids": fsbid_no_bids_to_tmap(data.get("no_bids")),
        "classifications": fsbid_classifications_to_tmap(employee.get("classifications", [])),
        "current_assignment": current_assignment,
        "assignments": fsbid_assignments_to_tmap(assignments),
        "employee_profile_url": get_employee_profile_urls(employee.get("perdet_seq_num", None)),
        "languages": fsbid_languages_to_tmap(data.get('languages', []) or []),
        "available_bidder_details": {
            **data.get("details", {}),
            "is_shared": pydash.get(data, 'details.is_shared') == '1',
            "archived": pydash.get(data, 'details.archived') == '1',
        }
    }
    return res

def convert_available_bidder_query(query):
    sort_asc = query.get("ordering", "name")[0] != "-"
    ordering = query.get("ordering", "name").lstrip("-")
    values = {
        "order_by": ordering,
        "is_asc": 'true' if sort_asc else 'false',
        "ad_id": query.get("ad_id", None),
    }

    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
