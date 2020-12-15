import logging
import csv

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

import talentmap_api.fsbid.services.client as client_services
from talentmap_api.cdo.models import AvailableBidders


logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders(jwt_token):
    '''
    Returns all clients in Available Bidders list
    '''
    perdet_ids = AvailableBidders.objects.values_list("bidder_perdet", flat=True)
    clients = []
    for per in perdet_ids:
        clients.append(client_services.single_client(jwt_token, per))

    return clients


def get_available_bidders_csv(jwt_token):
    '''
    Returns csv format of all users in Available Bidders list
    '''
    data = get_available_bidders(jwt_token)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=Available_Bidders_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        # smart_str(u"Skill"),
        smart_str(u"Grade"),
        smart_str(u"Employee ID"),
        smart_str(u"Position Location"),
        smart_str(u"Has Handshake"),
    ])

    for record in data:
        # print(record["skills"][0]["description"]),
        # print(record["skills"]),
        writer.writerow([
            smart_str(record["name"]),
            # smart_str(record["skills"][0]["description"]),
            smart_str("=\"%s\"" % record["grade"]),
            smart_str("=\"%s\"" % record["employee_id"]),
            smart_str("=\"%s\"" % record["pos_location"]),
            smart_str("=\"%s\"" % record["hasHandshake"]),
        ])
    return response
