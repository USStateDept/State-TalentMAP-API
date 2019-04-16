import requests
import logging

from django.conf import settings


logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL

def user_bids(employee_id, position_id=None):
  '''
    Get bids for a user on a position or all if no position
  '''
  bids = requests.get(f"{API_ROOT}/bids/?employeeId={employee_id}").json()
  return [bid for bid in bids if bid['cyclePosition']['cp_id'] == int(position_id)] if position_id else bids

def bid_on_position(userId, employeeId, cyclePositionId):
  '''
    Submits a bid on a position
  '''
  return requests.post(f"{API_ROOT}/bids", data = { "perdet_seq_num": employeeId, "cp_id": cyclePositionId, "userId": userId })

def remove_bid(employeeId, cyclePositionId):
  return requests.delete(f"{API_ROOT}/bids?cp_id={cyclePositionId}&perdet_seq_num={employeeId}")
