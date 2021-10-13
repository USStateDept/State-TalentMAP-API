import logging
import csv
import maya
import pydash

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

import talentmap_api.bureau.services.available_bidders as bureau_services
import talentmap_api.fsbid.services.client as client_services

from talentmap_api.common.common_helpers import ensure_date, formatCSV

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders_stats(data):
    '''
    Returns Available Bidders status statistics
    '''
    stats = {
        'Bureau': {}, # code comes through, but only with the short name/acronym
        'Grade': {},
        'Location': {}, # need to verify what this should be, Location or Post?
        # 'Post': {},
        'Skill': {},
        'Status': {},
        'TED': {},
    }
    # print('-------data-------')
    # print(data['results'][0]['skills'])
    # print('-------data-------')
    if data:
        # get stats for various fields
        for bidder in data['results']:
            stats['Grade'][bidder['grade']] = stats['Grade'].get(bidder['grade'], 0) + 1
            stats['Bureau'][bidder['current_assignment']['position']['bureau_code']] = stats['Bureau'].get(bidder['current_assignment']['position']['bureau_code'], 0) + 1
            stats['Location'][bidder['pos_location']] = stats['Location'].get(bidder['pos_location'], 0) + 1
            ted_key = smart_str(maya.parse(bidder['current_assignment']['end_date']).datetime().strftime('%m/%d/%Y'))
            stats['TED'][ted_key] = stats['TED'].get(ted_key, 0) + 1
            # stats['Skill'][bidder['skills']] = stats['Skill'].get(bidder['skills'], 0) + 1
            # if stat['skills'] is not '':
            #     stats['Skill'][stat['skills']] += 1
            if bidder['available_bidder_details']['status'] is not None:
                stats['Status'][bidder['available_bidder_details']['status']] = stats['Status'].get(bidder['available_bidder_details']['status'], 0) + 1

    print('------stats final update-------')
    print(stats)
    print('------stats update-------')
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
