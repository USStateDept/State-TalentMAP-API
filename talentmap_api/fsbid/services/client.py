import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def client(jwt_token):
    '''
    Get Clients by CDO
    '''
    # hru_id (cdo_id) is the unique identifier for get agents request 
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"Clients?ad_id={ad_id}"
    response = services.get_fsbid_results(uri, jwt_token, fsbid_clients_to_talentmap_clients)
    return response

def fsbid_clients_to_talentmap_clients(data):
    return {
        "id": data.get("hru_id", None),
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