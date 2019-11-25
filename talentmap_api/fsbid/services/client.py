import requests
import logging
import jwt

from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

# what do we need? 
# need to verify we have a cdo fetching the other cdos
# ad_id required for the req
# jwt required the req

# Are there any common methods that I'm missing? 
# Services are methods for the api calls? 
# Views are the actual controllers that map onto the RESTful API

# What do the views/controllers need?

def agents(jwt_token)
    '''
    Get All CDOs 
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/Client/Agents?ad_id={ad_id}&rl_cd=CDO"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    response.raise_for_status()
    return response

def fsbid_cdo_list_to_talentmap_cdo_list(data)
    return {
        "id": data.get("hru_id", None),
        "name": data.get("fullname", None),
        "email": data.get("email", None),
    }
