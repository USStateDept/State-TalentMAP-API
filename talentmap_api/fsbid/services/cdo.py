import logging
import jwt
import pydash
from django.conf import settings
import talentmap_api.fsbid.services.common as services
import talentmap_api.fsbid.services.client as clientServices
from talentmap_api.common.common_helpers import get_avatar_url

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)


def cdo(jwt_token):
    '''
    Get All CDOs
    '''
    from talentmap_api.fsbid.services.common import get_fsbid_results
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    email = jwt.decode(jwt_token, verify=False).get('email')
    uri = f"Agents?ad_id={ad_id}&request_params.rl_cd=CDO&request_params.rl_cd=CDO3"
    response = get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list, email)
    return response


def single_cdo(jwt_token=None, perdet_seq_num=None):
    '''
    Get a single CDO
    '''
    from talentmap_api.fsbid.services.common import get_fsbid_results
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    email = jwt.decode(jwt_token, verify=False).get('email')
    uri = f"Agents?ad_id={ad_id}&rl_cd=CDO&rl_cd=CDO3&request_params.perdet_seq_num={perdet_seq_num}"
    response = get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list, email)
    cdos = None

    if response is not None:
        cdos = list(response)

    if cdos and len(cdos) > 0:
        try:
            CDO = cdos[0]
            initials = "".join([x for x in CDO['email'] if x.isupper()][:2][::-1])
            CDO['initials'] = initials
            avatar = get_avatar_url(CDO['email'])
            CDO['avatar'] = avatar
        except:
            CDO = {}
    else:
        CDO = {}
    return CDO


def fsbid_cdo_list_to_talentmap_cdo_list(data):
    fullname = data.get("fullname", None)
    if fullname:
        fullname = fullname.rstrip(' NMN')

    return {
        "id": data.get("hru_id", None),
        "name": fullname,
        "email": data.get("email", None),
        "isCurrentUser": data.get("isCurrentUser", None),
    }


def insert_client_classification(jwt_token=None, perdet_seq_num=None, data=None):
    '''
    Inserts the client's classification
    '''
    te_id = ''
    count = 0

    for d in data:
        # te_id not coming through atm
        # need to change tracking detail to teid
        if len(data) > 1:
            if count != len(data) - 1 and count == 0:
                te_id = te_id + f"tracking_detail={d}"
                count += 1
            else:
                te_id = te_id + f"&tracking_detail={d}"
        else:
            te_id = te_id + f"tracking_detail={d}"

    uri = f"TrackingPrograms/bidders?{te_id}&perdet_seq_num={perdet_seq_num}"

    response = services.get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list)
    cdos = None

    if response is not None:
        cdos = list(response)


def delete_client_classification(jwt_token=None, perdet_seq_num=None, data=None):
    '''
    Deletes the client's classification
    '''
    te_id = ''
    count = 0
    for d in data:
        # te_id not coming through atm
        # need to change tracking detail to teid
        if len(data) > 1:
            if count != len(data) - 1 and count == 0:
                te_id = te_id + f"tracking_detail={d}"
                count += 1
            else:
                te_id = te_id + f"&tracking_detail={d}"
        else:
            te_id = te_id + f"tracking_detail={d}"

    uri = f"TrackingPrograms/bidders?{te_id}&perdet_seq_num={perdet_seq_num}"

    response = services.get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list)
    cdos = None

    if response is not None:
        cdos = list(response)


def fsbid_classifications_to_talentmap_classifications(data):
    return {
        # preliminary mapping setup
        "3": data.get("3rd Tour Bidders", None),
        "4": data.get("Tenured 4", None),
        "D": data.get("Differential Bidder", None),
        "T": data.get("Tandem Bidder", None),
        "M": data.get("Meritorious Step Increases", None),
        "6": data.get("6/8 Rule", None),
        "F": data.get("Fair Share Bidders", None),
        "C": data.get("Critical Need Language", None),
        "C1": data.get("Critical Need Language 1st Tour Complete", None),
        "CC": data.get("Critical Need Language Final Tour Complete", None),
        "R": data.get("Recommended for Tenure", None),
        "A": data.get("Ambassador or Deputy Assistant Secretary", None),
        "F1": data.get("Pickering Fellows", None),
        "F2": data.get("Rangel Fellows", None),
        "P": data.get("Pickering/Rangel Fellows", None),
    }
