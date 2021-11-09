import logging
import csv
import maya
import pydash
from copy import deepcopy

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

import talentmap_api.bureau.services.available_bidders as bureau_services
import talentmap_api.fsbid.services.client as client_services

from talentmap_api.common.common_helpers import ensure_date, formatCSV

from talentmap_api.common.common_helpers import formatCSV
from talentmap_api.fsbid.services.common import mapBool

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders_stats(data):
    '''
    Returns all Available Bidders statistics
    '''
    stats = {
        'Bureau': {},  # comes through, but only with the short name/acronym
        'Grade': {},
        'Post': {},
        'Skill': {},
        'Status': {},
        'TED': {},
    }
    stats_sum = {
        'Bureau': 0,
        'Grade': 0,
        'Post': 0,
        'Skill': 0,
        'Status': 0,
        'TED': 0,
    }

    if data:
        # get stats for various fields
        for bidder in pydash.get(data, 'results'):
            if bidder['current_assignment']['position']['bureau_code'] not in stats['Bureau']:
                stats['Bureau'][bidder['current_assignment']['position']['bureau_code']] = {'name': f"{bidder['current_assignment']['position']['bureau_code']}", 'value': 0}
            stats['Bureau'][bidder['current_assignment']['position']['bureau_code']]['value'] += 1
            stats_sum['Bureau'] += 1

            if bidder['grade'] not in stats['Grade']:
                stats['Grade'][bidder['grade']] = {'name': f"Grade {bidder['grade']}", 'value': 0}
            stats['Grade'][bidder['grade']]['value'] += 1
            stats_sum['Grade'] += 1

            if bidder['pos_location'] not in stats['Post']:
                stats['Post'][bidder['pos_location']] = {'name': f"{bidder['pos_location']}", 'value': 0}
            stats['Post'][bidder['pos_location']]['value'] += 1
            stats_sum['Post'] += 1

            skill = list(deepcopy(filter(None, bidder['skills'])))
            skill_key = skill[0]['code']
            if skill_key not in stats['Skill']:
                stats['Skill'][skill_key] = {'name': f"{skill[0]['description']}", 'value': 0}
            stats['Skill'][skill_key]['value'] += 1
            stats_sum['Skill'] += 1

            ab_status_key = bidder['available_bidder_details']['status']
            if ab_status_key is not None:
                if ab_status_key not in stats['Status']:
                    stats['Status'][ab_status_key] = {'name': f"{ab_status_key}", 'value': 0}
                stats['Status'][ab_status_key]['value'] += 1
                stats_sum['Status'] += 1

            ted_key = ensure_date(pydash.get(bidder, "current_assignment.end_date"), utc_offset=-5) or 'None listed'
            ted_key = "None listed" if ted_key is "None listed" else smart_str(maya.parse(ted_key).datetime().strftime('%m/%d/%Y'))
            if ted_key not in stats['TED']:
                stats['TED'][ted_key] = {'name': f"{ted_key}", 'value': 0}
            stats['TED'][ted_key]['value'] += 1
            stats_sum['TED'] += 1

    # adding percentage & creating final data structure to pass to FE
    biddersStats = {}
    for stat in stats:
        stat_sum = stats_sum[stat]
        biddersStats[stat] = []
        for s in stats[stat]:
            stat_value = stats[stat][s]['value']
            biddersStats[stat].append({**stats[stat][s], 'percent': "{:.0%}".format(stat_value / stat_sum)})

    biddersStats['Sum'] = stats_sum

    return {
        "stats": biddersStats,
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
            mapBool[fields["is_shared"]],
        ])

    return response
