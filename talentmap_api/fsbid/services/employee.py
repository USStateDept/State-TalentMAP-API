import requests
import logging
import jwt

from django.conf import settings
from django.contrib.auth.models import Group

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def get_employee_perdet_seq_num(jwt_token):
    '''
    Gets the perdet_seq_num for the employee from FSBid
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/Employees/userInfo?ad_id={ad_id}"
    employee = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return next(iter(employee.get('Data', [])), {}).get('perdet_seq_num')

def map_group_to_fsbid_role(jwt_token):
  '''
  Updates a user roles based on what we get back from FSBid
  '''
  role = jwt.decode(jwt_token, verify=False).get('role')
  return Group.objects.filter(name=ROLE_MAPPING.get(role)).first()

# Mapping of FSBid roles (keys) to TalentMap permissions (values)
ROLE_MAPPING = {
  "fsofficer": "bidder",
  "FSBidCycleAdministrator": "bidcycle_admin",
  "CDO": "cdo",
  "CDO3": "cdo",
}