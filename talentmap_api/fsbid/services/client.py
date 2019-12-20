import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
import csv
from datetime import datetime
from django.conf import settings
from urllib.parse import urlencode, quote
from django.http import HttpResponse
from django.utils.encoding import smart_str

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def client(jwt_token, hru_id, rl_cd):
    '''
    Get Clients by CDO
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"Clients?request_params.ad_id={ad_id}"
    if hru_id:
        uri = uri + f'&request_params.hru_id={hru_id}'
    if rl_cd:
        uri = uri + f'&request_params.rl_cd={rl_cd}'
    response = services.get_fsbid_results(uri, jwt_token, fsbid_clients_to_talentmap_clients)
    return response

def single_client(jwt_token, perdet_seq_num):
    '''
    Get a single client for a CDO
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"Clients?request_params.ad_id={ad_id}&request_params.perdet_seq_num={perdet_seq_num}"
    response = services.get_fsbid_results(uri, jwt_token, fsbid_clients_to_talentmap_clients)
    return list(response)[0]

def get_client_csv(query, jwt_token, rl_cd, host=None):
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    data = services.send_get_csv_request(
        "Clients",
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
        smart_str(u"Perdet Seq Number"),
        smart_str(u"Skill"),
        smart_str(u"Grade"),
        smart_str(u"Employee ID"),
        # smart_str(u"Role Code"), Might not be useful to users
        smart_str(u"Position Location Code"),
    ])

    for record in data:
        writer.writerow([
            smart_str(record["name"]),
            smart_str("=\"%s\"" % record["perdet_seq_number"]),
            smart_str(record["skills"]),
            smart_str("=\"%s\"" % record["grade"]),
            smart_str("=\"%s\"" % record["employee_id"]),
            # smart_str(record["role_code"]), Might not be useful to users
            smart_str("=\"%s\"" % record["pos_location_code"]),
        ])
    return response


def fsbid_clients_to_talentmap_clients(data):
    return {
        "id": data.get("perdet_seq_num", None),
        "name": data.get("per_full_name", None),
        "perdet_seq_number": data.get("perdet_seq_num", None),
        "grade": data.get("grade_code", None),
        "skills": map_skill_codes(data),
        "employee_id": data.get("emplid", None),
        "role_code": data.get("role_code", None),
        "pos_location_code": data.get("pos_location_code", None),
    }

def fsbid_clients_to_talentmap_clients_for_csv(data):
    return {
        "id": data.get("perdet_seq_num", None),
        "name": data.get("per_full_name", None),
        "perdet_seq_number": data.get("perdet_seq_num", None),
        "grade": data.get("grade_code", None),
        "skills": '\n'.join(map_skill_codes_for_csv(data)),
        "employee_id": data.get("emplid", None),
        "role_code": data.get("role_code", None),
        "pos_location_code": data.get("pos_location_code", None),
    }

def convert_client_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the client search filter naming
    '''
    values = {
        "request_params.hru_id": query.get("hru_id", None),
        "request_params.rl_cd": query.get("rl_cd", None),
        "request_params.ad_id": query.get("ad_id", None),
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.freeText": query.get("q", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

def map_skill_codes_for_csv(data):
    skills = []
    for i in range(1,4):
        index = i
        if i == 1:
            index = ''
        desc = data.get(f'skill{index}_code_desc', None)
        skills.append(desc)
    return filter(lambda x: x is not None, skills)

def map_skill_codes(data):
    skills = []
    for i in range(1,4):
        index = i
        if i == 1:
            index = ''
        code = data.get(f'skill{index}_code', None)
        desc = data.get(f'skill{index}_code_desc', None)
        skills.append({ 'code': code, 'description': desc })
    return filter(lambda x: x.get('code', None) is not None, skills)