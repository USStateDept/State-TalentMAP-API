import requests
import logging

from urllib.parse import urlencode

logger = logging.getLogger(__name__)

def get_pagination(query, count, base_url, host=None):
    '''
    Figures out all the pagination
    '''
    page = int(query.get("page", 0))
    limit = int(query.get("limit", 25))
    next_query = query.copy()
    next_query.__setitem__("page", page + 1)
    prev_query = query.copy()
    prev_query.__setitem__("page", page - 1)
    previous_url = f"{host}{base_url}{prev_query.urlencode()}" if host and page > 1 else None
    next_url = f"{host}{base_url}{next_query.urlencode()}" if host and page * limit < count else None
    return {
        "count": count,
        "next": next_url,
        "previous": previous_url
    }
