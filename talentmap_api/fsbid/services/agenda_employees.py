import logging
import jwt
import pydash
from urllib.parse import urlencode, quote

from django.conf import settings

from talentmap_api.fsbid.services import common as services


PERSON_API_ROOT = settings.PERSON_API_URL

logger = logging.getLogger(__name__)


def get_agenda_employees(query, jwt_token=None, host=None):
    '''
    Get employees
    '''
    args = {
        "uri": "agendaItems",
        "query": query,
        "query_mapping_function": convert_agenda_employees_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_agenda_employee_to_talentmap_agenda_employee,
        "count_function": False,
        "base_url": '',
        "host": host,
        "api_root": PERSON_API_ROOT,
        "use_post": False,
    }

    agenda_employees = services.send_get_request(
        **args
    )

    return agenda_employees

# TO-DO
# def get_agenda_employees_count(query, jwt_token, host=None, use_post=False):
#     '''
#     Get total number of employees for agenda search
#     '''
#     args = {
#         "uri": "",
#         "query": query,
#         "query_mapping_function": convert_agenda_employees_query,
#         "jwt_token": jwt_token,
#         "host": host,
#         "api_root": PERSON_API_ROOT,
#         "use_post": False,
#     }
#     return services.send_count_request(**args)

def convert_agenda_employees_query(query):
    '''
    Convert TalentMAP filters into FSBid filters
    '''
    filterValue = query.get("q", None)
    filterKey = ''
    comparator = 'eq'
    if filterValue:
        if filterValue.isdigit():
            filterKey = 'pertexternalid'
        else:
            filterKey = 'perpiifullname'
            comparator = 'contains'
            filterValue = filterValue.upper()

    values = {
        # Pagination
        "rp.pageNum": query.get("page", 1),
        "rp.pageRows": query.get("limit", 50),
        "rp.orderBy": "perpiifullname", # TODO - use services.sorting_values

        "rp.filter": services.convert_to_fsbid_ql(filterKey, filterValue, comparator),
        # services.convert_to_fsbid_ql('perdetseqnum', query.get("q", None)),
        # services.convert_to_fsbid_ql('perpiilastname', query.get("q", None)), TODO - passing multiples values
    }
    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_agenda_employee_to_talentmap_agenda_employee(data):
    '''
    Maps FSBid response to expected TalentMAP response
    '''
    current = data.get("currentAssignment", [])
    currentAssignment = pydash.get(current, '[0]') or {} if current else {}
    pos = pydash.get(currentAssignment, "position") or []
    position = pydash.get(pos, '[0]') or {} if pos else {}
    firstN = data.get('perpiifirstname', '')
    lastN = data.get('perpiilastname', '')
    initials = f"{firstN[0] if firstN else ''}{lastN[0] if lastN else ''}"
    fullName = data.get("perpiifullname", "")
    if pydash.ends_with(fullName, "NMN"):
        fullName = fullName.rstrip(" NMN")
    if pydash.ends_with(fullName, "Nmn"):
        fullName = fullName.rstrip(" Nmn")
    return {
        "person": {
            "lastName": lastN,
            "firstName": firstN,
            "middleName": data.get("perpiimiddlename", ""),
            "suffix": data.get("perpiisuffixname", ""),
            "fullName": fullName,
            "perdet": data.get("perdetseqnum", ""),
            "employeeID": data.get("pertexternalid", ""),
            "employeeSeqNumber": data.get("perpiiseqnum", ""),
            "orgCode": data.get("perdetorgcode", ""),
            "initials": initials,
            # data.get("perdetperscode", ""),
            # data.get("pertexternalid", ""),
            # data.get("perdetorgcode", ""),
            # data.get("pertcurrentind", ""),
            # data.get("perdetminactemplrcd#ind", ""),
            # data.get("persdesc", ""),
            # data.get("rnum", ""),
        },
        "currentAssignment": {
            "TED": currentAssignment.get("asgdetdteddate", ""),
            "TOD": currentAssignment.get("asgdtodcode", ""),
            "positionSequenceNumber": position.get("posseqnum", ""),
            "orgDescription": position.get("posorgshortdesc", ""),
            "positionNumber": position.get("posnumtext", ""),
            "grade": position.get("posgradecode", ""),
            "positionTitle": position.get("postitledesc", ""),
            # currentAssignment.get("asgperdetseqnum", ""),
            # currentAssignment.get("asgempseqnbr", ""),
            # currentAssignment.get("asgposseqnum", ""),
            # currentAssignment.get("asgdasgseqnum", ""),
            # currentAssignment.get("asgdrevisionnum", ""),
            # currentAssignment.get("asgdasgscode", ""),
            # currentAssignment.get("latestAgendaItem", []),
        }
    }
