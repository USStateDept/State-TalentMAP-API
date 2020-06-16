import requests
import re
import logging
import csv
from datetime import datetime
import maya

from urllib.parse import urlencode

from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.organization.models import Post, Organization, OrganizationGroup
from talentmap_api.settings import OBC_URL, OBC_URL_EXTERNAL

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
    next_url = f"{host}{base_url}{next_query.urlencode()}" if host and page * limit < int(count) else None
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

def parseLanguagesString(lang):
    '''
    Parses a language dictionary and turns it into a comma seperated string of languages
    '''
    if lang:
        lang_str = ""
        for l in lang:
            if not lang_str:
                lang_str = l["representation"]
            else:
                lang_str += ", " + l["representation"]

        return lang_str

def post_values(query):
    '''
    Handles mapping locations and groups of locations to FSBid expected params
    '''
    results = []
    if query.get("position__post__code__in"):
        results = results + query.get("position__post__code__in").split(',')
    if len(results) > 0:
        return results


def bureau_values(query, isTandem = False):
    '''
    Gets the ids for the functional/regional bureaus and maps to codes and their children
    '''
    org = "org_has_groups"
    bureau = "position__bureau__code__in"
    if (isTandem):
        org = "org_has_groups-tandem"
        bureau = "position__bureau__code__in-tandem"

    results = []
    # functional bureau filter
    if query.get(org):
        func_bureaus = query.get(org).split(",")
        func_org_codes = OrganizationGroup.objects.filter(id__in=func_bureaus).values_list("_org_codes", flat=True)
        # Flatten _org_codes
        func_bureau_codes = [item for sublist in func_org_codes for item in sublist]
        results = results + list(func_bureau_codes)
    # Regional bureau filter
    if query.get(bureau):
        regional_bureaus = query.get(bureau).split(",")
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
    "posted_date": "cp_post_dt",
    "skill": "skill",
    "grade": "grade",
    "client_skill": "per_skill_code",
    "client_grade": "per_grade_code",
    "client_last_name": "per_last_name",
    "client_first_name": "per_first_name",
    "location": "location_city",
    "commuterPost": "cpn_desc",
}


def sorting_values(sort):
    if sort is not None:
        results = []
        for s in sort.split(','):
            direction = 'asc'
            if s.startswith('-'):
                direction = 'desc'
                s = sort_dict.get(s[1:], None)
            else:
                s = sort_dict.get(s, None)
            if s is not None:
                results.append(f"{s} {direction}")
        return results


def get_results(uri, query, query_mapping_function, jwt_token, mapping_function):
    url = f"{API_ROOT}/{uri}?{query_mapping_function(query)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None
    return list(map(mapping_function, response.get("Data", {})))

def get_fsbid_results(uri, jwt_token, mapping_function, email=None):
    url = f"{API_ROOT}/{uri}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json() # nosec

    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None

    # determine if the result is the current user
    if email:
        for a in response.get("Data"):
            a['isCurrentUser'] = True if a.get('email', None) == email else False

    return map(mapping_function, response.get("Data", {}))


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
    newQuery = query.copy()
    countProp = "count(1)"
    if uri in ('CDOClients', 'positions/futureVacancies/tandem', 'positions/available/tandem'):
        newQuery['getCount'] = 'true'
        newQuery['request_params.page_index'] = None
        newQuery['request_params.page_size'] = None
    if uri in ('CDOClients'):
        countProp = "count"
    if uri in ('positions/futureVacancies/tandem', 'positions/available/tandem'):
        countProp = "cnt"
    url = f"{API_ROOT}/{uri}?{query_mapping_function(newQuery)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return {"count": response["Data"][0][countProp]}

def get_obc_id(post_id):

    post = Post.objects.filter(_location_code=post_id)
    if post.count() == 1:
        for p in post:
            return p.obc_id

    return None

def get_post_overview_url(post_id):
    obc_id = get_obc_id(post_id)
    if obc_id:
        return {
            'internal': f"{OBC_URL}/post/detail/{obc_id}",
            'external': f"{OBC_URL_EXTERNAL}/post/detail/{obc_id}"
        }
    else:
        return None

def get_post_bidding_considerations_url(post_id):
    obc_id = get_obc_id(post_id)
    if obc_id:
        return {
            'internal': f"{OBC_URL}/post/postdatadetails/{obc_id}",
            'external': f"{OBC_URL_EXTERNAL}/post/postdatadetails/{obc_id}"
        }
    else:
        return None

def send_get_csv_request(uri, query, query_mapping_function, jwt_token, mapping_function, base_url, host=None, ad_id=None, limit=None):
    '''
    Gets items from FSBid
    '''
    formattedQuery = query
    formattedQuery._mutable = True
    if (ad_id != None):
        formattedQuery['ad_id'] = ad_id
    if (limit != None):
        formattedQuery['limit'] = limit
    logger.info(query_mapping_function(formattedQuery))
    url = f"{API_ROOT}/{uri}?{query_mapping_function(formattedQuery)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None

    return map(mapping_function, response.get("Data", {}))

def get_ap_and_pv_csv(data, filename, ap=False, tandem=False):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename={filename}_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    headers = []
    headers.append(smart_str(u"Position"))
    if tandem: headers.append(smart_str(u"Tandem"))
    headers.append(smart_str(u"Skill"))
    headers.append(smart_str(u"Grade"))
    headers.append(smart_str(u"Bureau"))
    headers.append(smart_str(u"Post City"))
    headers.append(smart_str(u"Post Country"))
    headers.append(smart_str(u"Tour of Duty"))
    headers.append(smart_str(u"Languages"))
    if ap: headers.append(smart_str(u"Service Needs Differential"))
    headers.append(smart_str(u"Post Differential"))
    headers.append(smart_str(u"Danger Pay"))
    headers.append(smart_str(u"TED"))
    headers.append(smart_str(u"Incumbent"))
    headers.append(smart_str(u"Bid Cycle/Season"))
    if ap: headers.append(smart_str(u"Posted Date"))
    if ap: headers.append(smart_str(u"Status Code"))
    headers.append(smart_str(u"Position Number"))
    headers.append(smart_str(u"Capsule Description"))
    writer.writerow(headers)

    for record in data:
        try:
            ted = smart_str(maya.parse(record["ted"]).datetime().strftime('%m/%d/%Y'))
        except:
            ted = "None listed"
        try:
            posteddate = smart_str(maya.parse(record["posted_date"]).datetime().strftime('%m/%d/%Y')),
        except:
            posteddate = "None listed"

        row = []
        row.append(smart_str(record["position"]["title"]))
        if tandem: row.append(smart_str(record.get("tandem_nbr")))
        row.append(smart_str(record["position"]["skill"]))
        row.append(smart_str("=\"%s\"" % record["position"]["grade"]))
        row.append(smart_str(record["position"]["bureau"]))
        row.append(smart_str(record["position"]["post"]["location"]["city"]))
        row.append(smart_str(record["position"]["post"]["location"]["country"]))
        row.append(smart_str(record["position"]["tour_of_duty"]))
        row.append(smart_str(parseLanguagesString(record["position"]["languages"])))
        if ap: row.append(smart_str(record["position"]["post"].get("has_service_needs_differential")))
        row.append(smart_str(record["position"]["post"]["differential_rate"]))
        row.append(smart_str(record["position"]["post"]["danger_pay"]))
        row.append(ted)
        row.append(smart_str(record["position"]["current_assignment"]["user"]))
        row.append(smart_str(record["bidcycle"]["name"]))
        if ap: row.append(posteddate)
        if ap: row.append(smart_str(record.get("status_code")))
        row.append(smart_str("=\"%s\"" % record["position"]["position_number"]))
        row.append(smart_str(record["position"]["description"]["content"]))

        writer.writerow(row)
    return response

def get_bids_csv(data, filename, jwt_token):
    from talentmap_api.fsbid.services.available_positions import get_all_position

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename={filename}_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    headers = []
    headers.append(smart_str(u"Position"))
    headers.append(smart_str(u"Position Number"))
    headers.append(smart_str(u"Skill"))
    headers.append(smart_str(u"Grade"))
    headers.append(smart_str(u"Bureau"))
    headers.append(smart_str(u"Post City"))
    headers.append(smart_str(u"Post Country"))
    headers.append(smart_str(u"Tour of Duty"))
    headers.append(smart_str(u"Languages"))
    # headers.append(smart_str(u"Service Needs Differential"))
    headers.append(smart_str(u"Post Differential"))
    headers.append(smart_str(u"Danger Pay"))
    headers.append(smart_str(u"TED"))
    headers.append(smart_str(u"Incumbent"))
    headers.append(smart_str(u"Bid Cycle"))
    headers.append(smart_str(u"Bid Status"))
    headers.append(smart_str(u"Capsule Description"))

    writer.writerow(headers)

    for record in data:
        position_data = get_all_position(smart_str(record["position"]["id"]), jwt_token)
        if position_data is not None:
            try:
                ted = smart_str(maya.parse(position_data["ted"]).datetime().strftime('%m/%d/%Y'))
            except:
                ted = "None listed"

            row = []
            row.append(smart_str(record["position"]["title"]))
            row.append(smart_str("=\"%s\"" % record["position"]["position_number"]))
            row.append(smart_str(record["position"]["skill"]))
            row.append(smart_str("=\"%s\"" % record["position"]["grade"]))
            row.append(smart_str(position_data["position"]["bureau"]))
            row.append(smart_str(record["position"]["post"]["location"]["city"]))
            row.append(smart_str(record["position"]["post"]["location"]["country"]))
            row.append(smart_str(position_data["position"]["tour_of_duty"]))
            row.append(smart_str(parseLanguagesString(position_data["position"]["languages"])))
            # row.append(smart_str(position_data["position"]["post"].get("has_service_needs_differential")))
            row.append(smart_str(position_data["position"]["post"]["differential_rate"]))
            row.append(smart_str(position_data["position"]["post"]["danger_pay"]))
            row.append(ted)
            row.append(smart_str(position_data["position"]["current_assignment"]["user"]))
            row.append(smart_str(record["bidcycle"]))
            row.append(smart_str(record.get("status")))
            row.append(smart_str(position_data["position"]["description"]["content"]))

            writer.writerow(row)
    return response
