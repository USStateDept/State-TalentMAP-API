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
        "skill_code": data.get("skill_code", None),
        "skill_code_desc": data.get("skill_code_desc", None),
        "skill2_code": data.get("skill2_code", None),
        "skill2_code_desc": data.get("skill2_code_desc", None),
        "skill3_code": data.get("skill3_code", None),
        "skill3_code_desc": data.get("skill3_code_desc", None),
        "employee_id": data.get("emplid", None),
        "role_code": data.get("role_code", None),
        "pos_location_code": data.get("pos_location_code", None),
    }
