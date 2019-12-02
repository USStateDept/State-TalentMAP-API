import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def cdo(jwt_token):
    '''
    Get All CDOs 
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"/Agents?ad_id={ad_id}&rl_cd=CDO"
    respone = services.get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list)
    return response

def fsbid_cdo_list_to_talentmap_cdo_list(data):
    return {
        "id": data.get("hru_id", None),
        "name": data.get("fullname", None),
        "email": data.get("email", None),
    }