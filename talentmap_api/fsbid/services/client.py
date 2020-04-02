import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
import talentmap_api.fsbid.services.cdo as cdo_services
import talentmap_api.fsbid.services.available_positions as services_ap
import csv
from talentmap_api.common.common_helpers import ensure_date
from copy import deepcopy
from datetime import datetime
from django.conf import settings
from urllib.parse import urlencode, quote
from django.http import HttpResponse
from django.utils.encoding import smart_str

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def client(jwt_token, query, host=None):
    '''
    Get Clients by CDO
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"CDOClients"
    response = services.send_get_request(
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
    return services.send_count_request("CDOClients", query, convert_client_count_query, jwt_token, host)

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

    client = single_client(jwt_token, perdet_seq_num)
    grade = client.get("grade")
    skills = client.get("skills")
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
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"CDOClients?request_params.ad_id={ad_id}&request_params.perdet_seq_num={perdet_seq_num}&request_params.currentAssignmentOnly=false"
    response = services.get_fsbid_results(uri, jwt_token, fsbid_clients_to_talentmap_clients)
    cdo = cdo_services.single_cdo(jwt_token, perdet_seq_num)
    client = list(response)[0]
    client['cdo'] = cdo
    return client

def get_client_csv(query, jwt_token, rl_cd, host=None):
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    data = services.send_get_csv_request(
        "CDOClients",
        query,
        convert_client_query,
        jwt_token,
        fsbid_clients_to_talentmap_clients_for_csv,
        "/api/v1/fsbid/client/",
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
        smart_str(u"Skill"),
        smart_str(u"Grade"),
        smart_str(u"Employee ID"),
        # smart_str(u"Role Code"), Might not be useful to users
        smart_str(u"Position Location Code"),
    ])

    for record in data:
        writer.writerow([
            smart_str(record["name"]),
            smart_str(record["skills"]),
            smart_str("=\"%s\"" % record["grade"]),
            smart_str("=\"%s\"" % record["employee_id"]),
            # smart_str(record["role_code"]), Might not be useful to users
            smart_str("=\"%s\"" % record["pos_location"]),
        ])
    return response


def fsbid_clients_to_talentmap_clients(data):
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

    if current_assignment is not None and assignments and type(assignments) is type([]):
        # remove the current assignment, since we'll pass it with current_assignment
        assignments.pop(0)

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

    return {
        "id": employee.get("pert_external_id", None),
        "name": f"{employee.get('per_first_name', None)} {employee.get('per_last_name', None)}",
        "initials": initials,
        "perdet_seq_number": employee.get("perdet_seq_num", None),
        "grade": employee.get("per_grade_code", None),
        "skills": map_skill_codes(employee),
        "employee_id": employee.get("pert_external_id", None),
        "role_code": data.get("rl_cd", None),
        "pos_location": map_location(location),
        "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd")),
        "classifications": fsbid_classifications_to_tmap(employee.get("classifications", [])),
        "current_assignment": current_assignment,
        "assignments": fsbid_assignments_to_tmap(assignments)
    }

def fsbid_clients_to_talentmap_clients_for_csv(data):
    employee = data.get('employee', None)
    current_assignment = employee.get('currentAssignment', None)
    position = current_assignment.get('currentPosition', None)
    return {
        "id": employee.get("pert_external_id", None),
        "name": f"{employee.get('per_first_name', None)} {employee.get('per_last_name', None)}",
        "grade": employee.get("per_grade_code", None),
        "skills": ' , '.join(map_skill_codes_for_csv(employee)),
        "employee_id": employee.get("pert_external_id", None),
        "role_code": data.get("rl_cd", None),
        "pos_location": map_location(position.get("currentLocation", None)),
        "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd")),
        "classifications": fsbid_classifications_to_tmap(employee.get("classifications", []))
    }

def hru_id_filter(query):
    results = []
    hru_id = query.get("hru_id", None)
    results += [hru_id] if hru_id is not None else []
    hru_ids = services.convert_multi_value(query.get("hru_id__in", None))
    results += hru_ids if hru_ids is not None else []
    return results if len(results) > 0 else None

def convert_client_query(query, isCount = None):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the client search filter naming
    '''
    values = {
        "request_params.hru_id": hru_id_filter(query),
        "request_params.rl_cd": query.get("rl_cd", None),
        "request_params.ad_id": query.get("ad_id", None),
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.freeText": query.get("q", None),
        "request_params.bsn_id": services.convert_multi_value(query.get("bid_seasons")),
        "request_params.hs_cd": tmap_handshake_to_fsbid(query.get('hasHandshake', None)),
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

def map_skill_codes_for_csv(data, prefix = 'per'):
    skills = []
    for i in range(1,4):
        index = f'_{i}'
        if i == 1:
            index = ''
        desc = data.get(f'{prefix}_skill{index}_code_desc', None)
        skills.append(desc)
    return filter(lambda x: x is not None, skills)

def map_skill_codes(data):
    skills = []
    for i in range(1,4):
        index = f'_{i}'
        if i == 1:
            index = ''
        code = data.get(f'per_skill{index}_code', None)
        desc = data.get(f'per_skill{index}_code_desc', None)
        skills.append({ 'code': code, 'description': desc })
    return filter(lambda x: x.get('code', None) is not None, skills)

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
        "Y": "true",
        "N": "false",
    }
    return fsbid_dictionary.get(hs, None)

def tmap_handshake_to_fsbid(hs):
    # Maps TMap true/false value to acceptable fsbid api params for handshake
    tmap_dictionary = {
        "true": "Y",
        "false": "N"
    }
    return tmap_dictionary.get(hs, None)

def fsbid_classifications_to_tmap(cs):
    tmap_classifications = []
    if type(cs) is list:
        for x in cs:
            tmap_classifications.append(
                x.get('tp_code', None)
            )
    else:
        tmap_classifications.append(
            cs.get('tp_code', None),
        )
    return tmap_classifications

def fsbid_assignments_to_tmap(assignments):
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
                        "position_number":  pos.get('pos_seq_num', None),
                        "title": pos.get("pos_title_desc", None),
                        "post": {
                            "code": loc.get("gvt_geoloc_cd", None),
                            "post_overview_url": services.get_post_overview_url(loc.get("gvt_geoloc_cd", None)),
                            "post_bidding_considerations_url": services.get_post_bidding_considerations_url(loc.get("gvt_geoloc_cd", None)),
                            "obc_id": services.get_obc_id(loc.get("gvt_geoloc_cd", None)),
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
