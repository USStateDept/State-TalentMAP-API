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
    Returns Available Bidders status statistics
    '''
    ab = AvailableBidders.objects.all()
    stats = {
        'UA': 0,
        'IT': 0,
        'OC': 0,
        'AWOL': 0,
    }
    if ab:
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
        smart_str(u"Organization"),
        smart_str(u"City"),
        smart_str(u"State"),
        smart_str(u"Country"),
        smart_str(u"CDO Name"),
        smart_str(u"CDO Email"),
        smart_str(u"Comments"),
        smart_str(u"Shared with Bureau"),
    ])
    fields_info = {
        "name": None,
        "status": {"path": 'available_bidder_details.status', },
        "skills": {"default": "No Skills listed", "description_and_code": True},
        "grade": None,
        "ted": {"path": 'current_assignment.end_date', },
        "oc_bureau": {"path": 'available_bidder_details.oc_bureau', },
        "oc_reason": {"path": 'available_bidder_details.oc_reason', },
        "org": {"path": 'current_assignment.position.organization', },
        "city": {"path": 'current_assignment.position.post.location.city', },
        "state": {"path": 'current_assignment.position.post.location.state', },
        "country": {"path": 'current_assignment.position.post.location.country', },
        "comments": {"path": 'available_bidder_details.comments', },
        "is_shared": {"path": 'available_bidder_details.is_shared', },
        "cdo_email": {"path": 'cdo.email', },
    }

    for record in data["results"]:
        languages = f'' if pydash.get(record, "languages") else "None listed"
        if languages is not "None listed":
            for language in record["languages"]:
                languages += f'{language["custom_description"]}, '
        languages = languages.rstrip(', ')

        cdo_name = f'{pydash.get(record, "cdo.last_name")}, {pydash.get(record, "cdo.first_name")}'

        fields = formatCSV(record, fields_info)

        try:
            ted = maya.parse(fields["ted"]).datetime().strftime('%m/%d/%Y')
        except:
            ted = 'None listed'
        writer.writerow([
            fields["name"],
            fields["status"],
            fields["oc_bureau"],
            fields["oc_reason"],
            fields["skills"],
            smart_str("=\"%s\"" % fields["grade"]),
            languages,
            ted,
            fields["org"],
            fields["city"],
            fields["state"],
            fields["country"],
            cdo_name,
            fields["cdo_email"],
            fields["comments"],
            fields["is_shared"],
        ])

    return response
