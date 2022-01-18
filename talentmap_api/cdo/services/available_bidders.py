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
        'Bureau': {},
        'CDO': {},
        'Grade': {},
        'OC Bureau': {},
        'Post': {},
        'Skill': {},
        'Status': {},
    }
    stats_sum = {
        'Bureau': 0,
        'CDO': 0,
        'Grade': 0,
        'OC Bureau': 0,
        'Post': 0,
        'Skill': 0,
        'Status': 0,
    }

    none_listed = {'name': 'None listed', 'value': 0}

    if data:
        # get stats for various fields
        for bidder in pydash.get(data, 'results'):
            bureau_key = pydash.get(bidder, 'current_assignment.position.bureau_code')
            if bureau_key not in stats['Bureau']:
                stats['Bureau'][bureau_key] = deepcopy(none_listed) if bureau_key == None else {'name': f"{bureau_key}", 'value': 0}
            stats['Bureau'][bureau_key]['value'] += 1
            stats_sum['Bureau'] += 1

            cdo_full_name_key = pydash.get(bidder, 'cdo.full_name')
            if cdo_full_name_key not in stats['CDO']:
                stats['CDO'][cdo_full_name_key] = deepcopy(none_listed) if cdo_full_name_key == None else {'name': f"{cdo_full_name_key}", 'value': 0}
            stats['CDO'][cdo_full_name_key]['value'] += 1
            stats_sum['CDO'] += 1
            
            grade_key = pydash.get(bidder, 'grade')
            if grade_key not in stats['Grade']:
                stats['Grade'][grade_key] = deepcopy(none_listed) if grade_key == None else {'name': f"{grade_key}", 'value': 0}
            stats['Grade'][grade_key]['value'] += 1
            stats_sum['Grade'] += 1

            oc_bureau_key = pydash.get(bidder, 'available_bidder_details.oc_bureau')
            if oc_bureau_key not in stats['OC Bureau']:
                stats['OC Bureau'][oc_bureau_key] = deepcopy(none_listed) if oc_bureau_key == None else {'name': f"{oc_bureau_key}", 'value': 0}
            stats['OC Bureau'][oc_bureau_key]['value'] += 1
            stats_sum['OC Bureau'] += 1

            post_key = pydash.get(bidder, 'pos_location')
            if post_key not in stats['Post']:
                stats['Post'][post_key] = deepcopy(none_listed) if post_key == None else {'name': f"{post_key}", 'value': 0}
            stats['Post'][post_key]['value'] += 1
            stats_sum['Post'] += 1

            skill = list(deepcopy(filter(None, bidder['skills'])))
            skill_key = skill[0]['code']
            if skill_key not in stats['Skill']:
                stats['Skill'][skill_key] = deepcopy(none_listed) if skill_key == None else {'name': f"{skill[0]['description']}", 'value': 0}
            stats['Skill'][skill_key]['value'] += 1
            stats_sum['Skill'] += 1

            status_key = pydash.get(bidder, 'available_bidder_details.status')
            if status_key not in stats['Status']:
                stats['Status'][status_key] = deepcopy(none_listed) if status_key == None else {'name': f"{status_key}", 'value': 0}
            stats['Status'][status_key]['value'] += 1
            stats_sum['Status'] += 1

    # adding percentage & creating final data structure to pass to FE
    bidders_stats = {}
    for stat in stats:
        stat_sum = stats_sum[stat]
        bidders_stats[stat] = []
        for s in stats[stat]:
            stat_value = stats[stat][s]['value']
            bidders_stats[stat].append({**stats[stat][s], 'percent': "{:.0%}".format(stat_value / stat_sum)})

    # partition is used to handle the edge case when
    # len(bidders_stats['Post']) > 18 and all the post only have a value of 1
    # 18 was chosen due to UI Columns
    if len(bidders_stats['Post']) > 18:
        post_partition = pydash.partition(bidders_stats['Post'], lambda post: post['value'] > 1)
        take_from_pp = 18 - len(post_partition[0])
        post_partition[0].extend(post_partition[1][:take_from_pp])
        bidders_stats['Post'] = post_partition[0]
    
    bidders_stats['Grade'] = sorted(bidders_stats['Grade'], key = lambda grade: grade['name'])
    bidders_stats['Skill'] = sorted(bidders_stats['Skill'], key = lambda skill: skill['name'])
    bidders_stats['Sum'] = stats_sum

    return {
        "stats": bidders_stats,
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
