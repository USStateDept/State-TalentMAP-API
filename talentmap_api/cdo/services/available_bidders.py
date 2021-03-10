import logging
import csv
import maya
import pydash

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

from talentmap_api.cdo.models import AvailableBidders
import talentmap_api.bureau.services.available_bidders as bureau_services
import talentmap_api.fsbid.services.client as client_services

from talentmap_api.common.common_helpers import formatCSV

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders_stats():
    '''
    Returns Available Bidders list
    '''
    ab = AvailableBidders.objects.all()
    stats = {
        'UA': 0,
        'IT': 0,
        'OC': 0,
        'AWOL': 0,
    }
    if len(ab) > 0:
        results = ab.values('bidder_perdet', 'status', 'oc_reason', 'oc_bureau', 'comments', 'is_shared')
        # get stats for status field
        for stat in ab.values('status'):
            if stat['status'] is not '':
                stats[stat['status']] += 1
    return {
        "stats": stats
    }


def get_available_bidders_csv(request):
    '''
    Returns csv format of Available Bidders list
    '''
    data = client_services.get_available_bidders(request.META['HTTP_JWT'], True, request.query_params, f"{request.scheme}://{request.get_host()}")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=Available_Bidders_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Status"),
        smart_str(u"OC Bureau"),
        smart_str(u"OC Reason"),
        smart_str(u"Skills"),
        smart_str(u"Grade"),
        smart_str(u"Languages"),
        smart_str(u"TED"),
        smart_str(u"Post"),
        # smart_str(u"CDO"),
        smart_str(u"Comments"),
        smart_str(u"Shared with Bureau"),
    ])
    fields_info = {
        "name": None,
        "status": {"path": 'available_bidder_details.status', },
        "skills": {"default": "No Skills listed", },
        "grade": None,
        "TED": {"path": 'current_assignment.end_date', },
        "oc_bureau": {"path": 'available_bidder_details.oc_bureau', },
        "oc_reason": {"path": 'available_bidder_details.oc_reason', },
        "comments": {"path": 'available_bidder_details.comments', },
        "is_shared": {"path": 'available_bidder_details.is_shared', },
    }

    for record in data["results"]:
        # special Post Handling
        post_location = pydash.get(record, ["current_assignment.position.post.location"])
        post = None
        if post_location is None:
            post = "None listed"
        elif post_location["state"] is "DC":
            # DC Post - org ex.GTM / EX / SDD
            post = record["current_assignment"]["position"]["organization"]
        elif post_location["country"] is "USA":
            # Domestic Post outside of DC - City, State
            post = f'{post_location["city"]}, {post_location["state"]}'
        else:
            # Foreign Post - City, Country
            post = f'{post_location["city"]}, {post_location["country"]}'

        languages = f'' if pydash.get(record, ["languages"]) else "None listed"
        if languages is not "None listed":
            for language in record["languages"]:
                languages += f'{language["custom_description"]},'
        languages = languages.rstrip(',')

        # cdo = f'{record["cdo_last_name"]}, {record["cdo_first_name"]}'

        fields = formatCSV(record, fields_info)
        writer.writerow([
            fields["name"],
            fields["status"],
            fields["oc_bureau"],
            fields["oc_reason"],
            fields["skills"],
            smart_str("=\"%s\"" % fields["grade"]),
            languages,
            maya.parse(fields["TED"]).datetime().strftime('%m/%d/%Y'),
            post,
            # cdo,
            fields["comments"],
            fields["is_shared"],
        ])
    return response
