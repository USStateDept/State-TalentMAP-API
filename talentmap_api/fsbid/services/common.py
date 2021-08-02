import re
import logging
import csv
from datetime import datetime
import requests

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.http import QueryDict

import maya
import pydash

from talentmap_api.organization.models import Obc
from talentmap_api.settings import OBC_URL, OBC_URL_EXTERNAL

from talentmap_api.available_positions.models import AvailablePositionFavorite, AvailablePositionRanking
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite
from talentmap_api.available_tandem.models import AvailableFavoriteTandem
from talentmap_api.projected_tandem.models import ProjectedFavoriteTandem
from talentmap_api.fsbid.services import available_positions as apservices
from talentmap_api.fsbid.services import projected_vacancies as pvservices
from talentmap_api.fsbid.services import employee as empservices

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL
CP_API_ROOT = settings.CP_API_URL
HRDATA_URL = settings.HRDATA_URL
HRDATA_URL_EXTERNAL = settings.HRDATA_URL_EXTERNAL
FAVORITES_LIMIT = settings.FAVORITES_LIMIT

def get_employee_profile_urls(clientid):
    suffix = f"Employees/{clientid}/EmployeeProfileReportByCDO"
    return {
        "internal": f"{HRDATA_URL}/{suffix}",
        "external": f"{HRDATA_URL_EXTERNAL}/{suffix}",
    }


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
    toReturn = None
    if val is not None:
        toReturn = val.split(',')
    if toReturn is not None and len(toReturn[0]) is 0:
        toReturn = None
    return toReturn


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
    "location_city": "geoloc.city",
    "location_country": "geoloc.country",
    "location_state": "geoloc.state",
    "commuterPost": "cpn_desc",
    "tandem": "tandem_nbr",
    "bidder_grade": "grade_code",
    "bidder_skill": "skill_desc",
    "bidder_hs": "handshake_code",
    # Check fsbid to confirm these mappings work
    "bidder_language": "language_txt",
    "bidder_ted": "TED",
    "bidder_name": "full_name",
    "bidder_bid_submitted_date": "bid_submit_date",
}


mapBool = {True: 'Yes', False: 'No', 'default': ''}


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


def get_results(uri, query, query_mapping_function, jwt_token, mapping_function, api_root=API_ROOT):
    queryClone = query or {}
    if query_mapping_function:
        url = f"{api_root}/{uri}?{query_mapping_function(queryClone)}"
    else:
        url = f"{api_root}/{uri}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None
    if mapping_function:
        return list(map(mapping_function, response.get("Data", {})))
    else:
        return response.get("Data", {})


def get_fsbid_results(uri, jwt_token, mapping_function, email=None):
    url = f"{API_ROOT}/{uri}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None

    # determine if the result is the current user
    if email:
        for a in response.get("Data"):
            a['isCurrentUser'] = True if a.get('email', None) == email else False

    return map(mapping_function, response.get("Data", {}))


def get_individual(uri, id, query_mapping_function, jwt_token, mapping_function, api_root=API_ROOT):
    '''
    Gets an individual record by the provided ID
    '''
    response = get_results(uri, {"id": id}, query_mapping_function, jwt_token, mapping_function, api_root)
    return pydash.get(response, '[0]') or None


def send_get_request(uri, query, query_mapping_function, jwt_token, mapping_function, count_function, base_url, host=None, api_root=API_ROOT):
    '''
    Gets items from FSBid
    '''
    pagination = get_pagination(query, count_function(query, jwt_token)['count'], base_url, host) if count_function else {}
    return {
        **pagination,
        "results": get_results(uri, query, query_mapping_function, jwt_token, mapping_function, api_root)
    }


def send_count_request(uri, query, query_mapping_function, jwt_token, host=None, api_root=API_ROOT):
    '''
    Gets the total number of items for a filterset
    '''
    newQuery = query.copy()
    countProp = "count(1)"
    if uri in ('CDOClients', 'positions/futureVacancies/tandem', 'positions/available/tandem', 'cyclePositions'):
        newQuery['getCount'] = 'true'
        newQuery['request_params.page_index'] = None
        newQuery['request_params.page_size'] = None
    if uri in 'CDOClients':
        countProp = "count"
    if uri in ('positions/futureVacancies/tandem', 'positions/available/tandem'):
        countProp = "cnt"
    url = f"{api_root}/{uri}?{query_mapping_function(newQuery)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return {"count": response["Data"][0][countProp]}


# pre-load since this data rarely changes
obc_vals = list([])

def get_obc_vals():
    global obc_vals
    if not obc_vals:
        obc_vals = list(Obc.objects.values())
    return obc_vals

def get_obc_id(post_id):
    obc = pydash.find(get_obc_vals(), lambda x: x['code'] == post_id)

    if obc:
        return obc['obc_id']

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
    if ad_id is not None:
        formattedQuery['ad_id'] = ad_id
    if limit is not None:
        formattedQuery['limit'] = limit
    url = f"{base_url}/{uri}?{query_mapping_function(formattedQuery)}"
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
    if tandem:
        headers.append(smart_str(u"Tandem"))
    headers.append(smart_str(u"Skill"))
    headers.append(smart_str(u"Grade"))
    headers.append(smart_str(u"Bureau"))
    headers.append(smart_str(u"Organization"))
    headers.append(smart_str(u"Post City"))
    headers.append(smart_str(u"Post Country"))
    headers.append(smart_str(u"Tour of Duty"))
    headers.append(smart_str(u"Languages"))
    if ap:
        headers.append(smart_str(u"Service Needs Differential"))
    headers.append(smart_str(u"Post Differential"))
    headers.append(smart_str(u"Danger Pay"))
    headers.append(smart_str(u"TED"))
    headers.append(smart_str(u"Incumbent"))
    headers.append(smart_str(u"Bid Cycle/Season"))
    if ap:
        headers.append(smart_str(u"Posted Date"))
    if ap:
        headers.append(smart_str(u"Status Code"))
    headers.append(smart_str(u"Position Number"))
    headers.append(smart_str(u"Capsule Description"))
    writer.writerow(headers)

    for record in data:
        try:
            ted = smart_str(maya.parse(record["ted"]).datetime().strftime('%m/%d/%Y'))
        except:
            ted = "None listed"
        try:
            posteddate = smart_str(maya.parse(record["posted_date"]).datetime().strftime('%m/%d/%Y'))
        except:
            posteddate = "None listed"

        row = []
        row.append(smart_str(record["position"]["title"]))
        if tandem:
            row.append(smart_str(record.get("tandem_nbr")))
        row.append(smart_str(record["position"]["skill"]))
        row.append(smart_str("=\"%s\"" % record["position"]["grade"]))
        row.append(smart_str(record["position"]["bureau"]))
        row.append(smart_str(record["position"]["organization"]))
        row.append(smart_str(record["position"]["post"]["location"]["city"]))
        row.append(smart_str(record["position"]["post"]["location"]["country"]))
        row.append(smart_str(record["position"]["tour_of_duty"]))
        row.append(smart_str(parseLanguagesString(record["position"]["languages"])))
        if ap:
            row.append(smart_str(record["position"]["post"].get("has_service_needs_differential")))
        row.append(smart_str(record["position"]["post"]["differential_rate"]))
        row.append(smart_str(record["position"]["post"]["danger_pay"]))
        row.append(ted)
        row.append(smart_str(record["position"]["current_assignment"]["user"]))
        row.append(smart_str(record["bidcycle"]["name"]))
        if ap:
            row.append(posteddate)
        if ap:
            row.append(smart_str(record.get("status_code")))
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
    headers.append(smart_str(u"Service Need Differential"))
    headers.append(smart_str(u"Handshake Offered"))
    headers.append(smart_str(u"Difficult to Staff"))
    headers.append(smart_str(u"Post Differential"))
    headers.append(smart_str(u"Danger Pay"))
    headers.append(smart_str(u"TED"))
    headers.append(smart_str(u"Incumbent"))
    headers.append(smart_str(u"Bid Cycle"))
    headers.append(smart_str(u"Bid Status"))
    headers.append(smart_str(u"Handshake Status"))
    headers.append(smart_str(u"Handshake Accepted/Declined by CDO"))
    headers.append(smart_str(u"Capsule Description"))

    writer.writerow(headers)

    for record in data:
        if record["position_info"] is not None:
            try:
                ted = smart_str(maya.parse(record["position_info"]["ted"]).datetime().strftime('%m/%d/%Y'))
            except:
                ted = "None listed"
            hs_status = (pydash.get(record, 'handshake.hs_status_code') or '').replace('_', ' ')
            row = []
            row.append(smart_str(record["position_info"]["position"]["title"]))
            row.append(smart_str("=\"%s\"" % record["position_info"]["position"]["position_number"]))
            row.append(smart_str(record["position_info"]["position"]["skill"]))
            row.append(smart_str("=\"%s\"" % record["position_info"]["position"]["grade"]))
            row.append(smart_str(record["position_info"]["position"]["bureau"]))
            row.append(smart_str(record["position_info"]["position"]["post"]["location"]["city"]))
            row.append(smart_str(record["position_info"]["position"]["post"]["location"]["country"]))
            row.append(smart_str(record["position_info"]["position"]["tour_of_duty"]))
            row.append(smart_str(parseLanguagesString(record["position_info"]["position"]["languages"])))
            row.append(smart_str(record["position_info"]["isServiceNeedDifferential"]))
            row.append(smart_str(record["position_info"]["bid_statistics"][0]["has_handshake_offered"]))
            row.append(smart_str(record["position_info"]["isDifficultToStaff"]))
            row.append(smart_str(record["position_info"]["position"]["post"]["differential_rate"]))
            row.append(smart_str(record["position_info"]["position"]["post"]["danger_pay"]))
            row.append(ted)
            row.append(smart_str(record["position_info"]["position"]["current_assignment"]["user"]))
            row.append(smart_str(record["position_info"]["bidcycle"]["name"]))
            if record.get("status") == "handshake_accepted":
                row.append(smart_str("handshake_registered"))
            else:
                row.append(smart_str(record.get("status")))
            row.append(hs_status)
            row.append(mapBool[pydash.get(record, "handshake.hs_cdo_indicator", 'default')])
            row.append(smart_str(record["position_info"]["position"]["description"]["content"]))

            writer.writerow(row)
    return response


def archive_favorites(ids, request, isPV=False, favoritesLimit=FAVORITES_LIMIT):
    fav_length = len(ids)
    if fav_length >= favoritesLimit or fav_length == round(favoritesLimit / 2):
        # Pos nums is string to pass correctly to services url
        pos_nums = ','.join(ids)
        # List favs is list of integers instead of strings for comparison
        list_favs = list(map(lambda x: int(x), ids))
        # Ids from fsbid that are returned
        if isPV:
            returned_ids = pvservices.get_pv_favorite_ids(QueryDict(f"id={pos_nums}&limit=999999&page=1"), request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        else:
            returned_ids = apservices.get_ap_favorite_ids(QueryDict(f"id={pos_nums}&limit=999999&page=1"), request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        # Need to determine which ids need to be archived using comparison of lists above
        outdated_ids = []
        if isinstance(returned_ids, list):
            for fav_id in list_favs:
                if fav_id not in returned_ids:
                    outdated_ids.append(fav_id)
            if len(outdated_ids) > 0:
                if isPV:
                    ProjectedVacancyFavorite.objects.filter(fv_seq_num__in=outdated_ids).update(archived=True)
                    ProjectedFavoriteTandem.objects.filter(fv_seq_num__in=outdated_ids).update(archived=True)
                else:
                    AvailablePositionFavorite.objects.filter(cp_id__in=outdated_ids).update(archived=True)
                    AvailableFavoriteTandem.objects.filter(cp_id__in=outdated_ids).update(archived=True)

# Determine if the bidder has a competing #1 ranked bid on a position within the requester's org or bureau permissions
def has_competing_rank(jwt, perdet, pk):
    rankOneBids = AvailablePositionRanking.objects.filter(bidder_perdet=perdet, rank=0).exclude(cp_id=pk).values_list(
        "cp_id", flat=True)
    for y in rankOneBids:
        hasBureauPermissions = empservices.has_bureau_permissions(y, jwt)
        hasOrgPermissions = empservices.has_org_permissions(y, jwt)
        if hasBureauPermissions or hasOrgPermissions:
            # don't bother continuing the loop if we've already found one
            return True
    return False

def get_bidders_csv(self, pk, data, filename, jwt_token):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename={filename}_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    headers = []
    headers.append(smart_str(u"Name"))
    headers.append(smart_str(u"Deconflict"))
    headers.append(smart_str(u"Submitted Date"))
    headers.append(smart_str(u"Has Handshake"))
    headers.append(smart_str(u"Skill"))
    headers.append(smart_str(u"Grade"))
    headers.append(smart_str(u"Language"))
    headers.append(smart_str(u"TED"))
    headers.append(smart_str(u"CDO"))
    headers.append(smart_str(u"CDO Email"))
    headers.append(smart_str(u"Handshake Status"))
    headers.append(smart_str(u"Handshake Accepted/Declined by CDO"))

    writer.writerow(headers)

    for record in data:
        try:
            ted = smart_str(maya.parse(record["ted"]).datetime().strftime('%m/%d/%Y'))
        except:
            ted = "None listed"
        try:
            submit_date = smart_str(maya.parse(record["submitted_date"]).datetime().strftime('%m/%d/%Y'))
        except:
            submit_date = "None listed"
        try:
            cdo_name = smart_str(record["cdo"]["name"])
            cdo_email = smart_str(record["cdo"]["email"])
        except:
            cdo_name = ''
            cdo_email = ''

        hs_status = (pydash.get(record, 'handshake.hs_status_code') or '').replace('_', ' ')
        row = []
        row.append(smart_str(record["name"]))
        row.append(mapBool[pydash.get(record, 'has_competing_rank', 'default')])
        row.append(submit_date)
        row.append(mapBool[pydash.get(record, 'has_handshake_offered', 'default')])
        row.append(smart_str(record["skill"]))
        row.append(smart_str("=\"%s\"" % record["grade"]))
        row.append(smart_str(record["language"]))
        row.append(ted)
        row.append(cdo_name)
        row.append(cdo_email)
        row.append(hs_status)
        row.append(mapBool[pydash.get(record, "handshake.hs_cdo_indicator", 'default')])

        writer.writerow(row)
    return response
