import logging
import csv
import maya

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

import talentmap_api.fsbid.services.client as client_services
from talentmap_api.cdo.models import AvailableBidders


logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders(jwt_token, is_cdo):
    '''
    Returns all clients in Available Bidders list
    '''
    available_bidders = AvailableBidders.objects
    if is_cdo is False:
        available_bidders = available_bidders.filter(is_shared=True)
    perdet_ids = available_bidders.values_list("bidder_perdet", flat=True)
    clients = []
    for per in perdet_ids:
        clients.append(client_services.single_client(jwt_token, per))
    return clients


def get_available_bidders_csv(jwt_token, is_cdo):
    '''
    Returns csv format of all users in Available Bidders list
    '''
    data = get_available_bidders(jwt_token, is_cdo)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=Available_Bidders_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Skills"),
        smart_str(u"Grade"),
        smart_str(u"TED"),
        smart_str(u"Post"),
        smart_str(u"CDO"),
    ])

    for record in data:
        fields = {
            "name": None,
            "skills": None,
            "grade": None,
            "ted": None,
            "post": None,
            "cdo": None,
        }
        for f in fields:
            if f is "skills":
                skills = []
                for skill in list(record[f]):
                    skills.append(skill["description"])
                if not skills:
                    fields[f] = "No Skills listed"
                else:
                    fields[f] = ', '.join(skills)
            else:
                try:
                    if f is "ted":
                        fields[f] = maya.parse(record["current_assignment"]["end_date"]).datetime().strftime('%m/%d/%Y')
                    elif f is "post":
                        fields[f] = record["current_assignment"]["position"]["post"]["location"]["country"]
                    elif f is "cdo":
                        fields[f] = record["cdo"]["name"]
                    else:
                        fields[f] = record[f]
                except:
                    fields[f] = "None listed"
                finally:
                    if fields[f] is "":
                        fields[f] = "None listed"


        writer.writerow([
            fields["name"],
            fields["skills"],
            smart_str("=\"%s\"" % fields["grade"]),
            fields["ted"],
            fields["post"],
            fields["cdo"],
        ])
    return response
