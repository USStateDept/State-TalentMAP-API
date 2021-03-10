import logging
import csv
import maya
import pydash

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

import talentmap_api.fsbid.services.client as client_services
from talentmap_api.cdo.models import AvailableBidders

from talentmap_api.common.common_helpers import formatCSV

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders(jwt_token, is_cdo):
    '''
    Returns all clients in Available Bidders list
    '''
    # deprecated??
    available_bidders = AvailableBidders.objects
    if is_cdo is False:
        available_bidders = available_bidders.filter(is_shared=True)
    perdet_ids = available_bidders.values_list("bidder_perdet", flat=True)
    clients = []
    for per in perdet_ids:
        clients.append(client_services.single_client(jwt_token, per))
    return clients


def get_available_bidders_csv(request):
    '''
    Returns csv format of all users in Available Bidders list
    '''
    data = client_services.get_available_bidders(request.META['HTTP_JWT'], False, request.query_params, f"{request.scheme}://{request.get_host()}")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=Available_Bidders_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Skills"),
        smart_str(u"Grade"),
        smart_str(u"Languages"),
        smart_str(u"TED"),
        smart_str(u"Organization"),
        smart_str(u"City"),
        smart_str(u"State"),
        smart_str(u"Country"),
        smart_str(u"CDO"),
    ])

    fields_info = {
        "name": None,
        "skills": {"default": "No Skills listed", },
        "grade": None,
        "ted": {"path": 'current_assignment.end_date', },
        "org": {"path": 'current_assignment.position.organization', },
        "city": {"path": 'current_assignment.position.post.location.city', },
        "state": {"path": 'current_assignment.position.post.location.state', },
        "country": {"path": 'current_assignment.position.post.location.country', },
    }

    for record in data["results"]:
        languages = f'' if pydash.get(record, ["languages"]) else "None listed"
        if languages is not "None listed":
            for language in record["languages"]:
                languages += f'{language["custom_description"]},'
        languages = languages.rstrip(',')

        cdo = f'{pydash.get(record, "cdo.last_name")}, {pydash.get(record, "cdo.first_name")}'

        fields = formatCSV(record, fields_info)
        writer.writerow([
            fields["name"],
            fields["skills"],
            smart_str("=\"%s\"" % fields["grade"]),
            languages,
            maya.parse(fields["ted"]).datetime().strftime('%m/%d/%Y'),
            fields["org"],
            fields["city"],
            fields["state"],
            fields["country"],
            cdo,
        ])
    return response
