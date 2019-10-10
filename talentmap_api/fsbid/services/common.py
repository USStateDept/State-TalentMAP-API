import requests
import re
import logging

from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q

from talentmap_api.organization.models import Post, Organization, OrganizationGroup

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


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


def convert_multi_value(val):
    if val is not None:
        return val.split(',')


# Pattern for extracting language parts from a string. Ex. "Spanish(SP) (3/3)"
LANG_PATTERN = re.compile("(.*?)(\(.*\))\s(\d)/(\d)")


def parseLanguage(lang):
    '''
    Parses a language string from FSBid and turns it into what we want
    The lang param comes in as something like "Spanish(SP) 3/3"
    '''
    if lang:
        match = LANG_PATTERN.search(lang)
        if match:
            language = {}
            language["language"] = match.group(1)
            language["reading_proficiency"] = match.group(3)
            language["spoken_proficiency"] = match.group(4)
            language["representation"] = f"{match.group(1)} {match.group(2)} {match.group(3)}/{match.group(4)}"
            return language


def post_values(query):
    '''
    Handles mapping locations and groups of locations to FSBid expected params
    '''
    results = []
    if query.get("position__post__in"):
        post_ids = query.get("position__post__in").split(",")
        location_codes = Post.objects.filter(id__in=post_ids).values_list("_location_code", flat=True)
        results = results + list(location_codes)
    if query.get("position__post__code__in"):
        results = results + query.get("position__post__code__in").split(',')
    if len(results) > 0:
        return results


def bureau_values(query):
    '''
    Gets the ids for the functional/regional bureaus and maps to codes and their children
    '''
    results = []
    # functional bureau filter
    if query.get("org_has_groups"):
        func_bureaus = query.get("org_has_groups").split(",")
        func_org_codes = OrganizationGroup.objects.filter(id__in=func_bureaus).values_list("_org_codes", flat=True)
        # Flatten _org_codes
        func_bureau_codes = [item for sublist in func_org_codes for item in sublist]
        results = results + list(func_bureau_codes)
    # Regional bureau filter
    if query.get("position__bureau__code__in"):
        regional_bureaus = query.get("position__bureau__code__in").split(",")
        reg_org_codes = Organization.objects.filter(Q(code__in=regional_bureaus) | Q(_parent_organization_code__in=regional_bureaus)).values_list("code", flat=True)
        results = results + list(reg_org_codes)
    if len(results) > 0:
        return results


def overseas_values(query):
    '''
    Maps the overseas/domestic filter to the proper value
    '''
    if query.get("is_domestic") == "true":
        return "D"
    if query.get("is_domestic") == "false":
        return "O"


sort_dict = {
    "position__title": "pos_title_desc",
    "position__grade": "pos_grade_code",
    "position__bureau": "pos_bureau_short_desc",
    "ted": "ted",
    "position__position_number": "pos_num_text",
    "posted_date": "cp_post_dt"
}


def sorting_values(sort):
    if sort is not None:
        direction = 'asc'
        if sort.startswith('-'):
            direction = 'desc'
            sort = sort_dict.get(sort[1:], None)
        else:
            sort = sort_dict.get(sort, None)
        if sort is not None:
            return f"{sort} {direction}"


def get_results(uri, query, query_mapping_function, jwt_token, mapping_function):
    url = f"{API_ROOT}/{uri}?{query_mapping_function(query)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    return list(map(mapping_function, response["Data"]))

def get_fsbid_results(uri, jwt_token, mapping_function):
    url = f"{API_ROOT}/{uri}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json() # nosec
    
    return map(mapping_function, response["Data"])

def get_individual(uri, id, query_mapping_function, jwt_token, mapping_function):
    '''
    Gets an individual record by the provided ID
    '''
    return next(iter(get_results(uri, {"id": id}, query_mapping_function, jwt_token, mapping_function)), None)


def send_get_request(uri, query, query_mapping_function, jwt_token, mapping_function, count_function, base_url, host=None):
    '''
    Gets items from FSBid
    '''
    return {
        **get_pagination(query, count_function(query, jwt_token)['count'], base_url, host),
        "results": get_results(uri, query, query_mapping_function, jwt_token, mapping_function)
    }


def send_count_request(uri, query, query_mapping_function, jwt_token, host=None):
    '''
    Gets the total number of items for a filterset
    '''
    url = f"{API_ROOT}/{uri}?{query_mapping_function(query)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return {"count": response["Data"][0]["count(1)"]}


def send_get_csv_request(uri, query, query_mapping_function, jwt_token, mapping_function, base_url, host=None):
    '''
    Gets items from FSBid
    '''
    url = f"{API_ROOT}/{uri}?{query_mapping_function(query)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()

    results = map(mapping_function, response["Data"])
    return results
