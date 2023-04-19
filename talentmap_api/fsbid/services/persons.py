import pydash
from talentmap_api.fsbid.services import common as services
from urllib.parse import urlencode, quote
from django.conf import settings

PERSON_API_ROOT = settings.PERSON_API_URL

def get_persons(pk, jwt_token=None, host=None):
    '''
    Get an employee by perdetseqnum from v3/persons
    '''
    args = {
        "uri": "",
        "query": {'perdetseqnum': pk},
        "query_mapping_function": convert_v3_persons_query,
        "jwt_token": jwt_token,
        'mapping_function': persons_to_tm,
        "count_function": None,
        "base_url": '',
        "host": host,
        "api_root": PERSON_API_ROOT,
        "use_post": False,
    }

    agenda_employees = services.send_get_request(
        **args
    )

    return agenda_employees

def convert_v3_persons_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1)),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'perdetseqnum', 'val': query.get("perdetseqnum")},
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def persons_to_tm(data):
    firstN = data.get('perpiifirstname', '')
    lastN = data.get('perpiilastname', '')
    name = firstN +' '+ lastN

    return {
      'name': name,
      'perdet_seq_number': str(data.get('perdetseqnum', '')),
    }
