import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
from django.conf import settings

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