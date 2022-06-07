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

    config = [
        { 'key': 'current_assignment.position.bureau_code', 'statsKey': 'Bureau' },
        { 'key': 'cdo.full_name', 'statsKey': 'CDO' },
        { 'key': 'grade', 'statsKey': 'Grade' },
        { 'key': 'available_bidder_details.oc_bureau', 'statsKey': 'OC Bureau' },
        { 'key': 'pos_location', 'statsKey': 'Post' },
        { 'key': 'skills', 'statsKey': 'Skill' },
        { 'key': 'available_bidder_details.status', 'statsKey': 'Status' },
    ]

    none_listed = {'name': 'None listed', 'value': 0}

    if data:
        # get stats for various fields
        for bidder in pydash.get(data, 'results'):
            def map_object(stat):
                key = pydash.get(bidder, stat['key'])
                stats_key = stats[stat['statsKey']]
                if stat['key'] == 'skills':
                    skill = list(deepcopy(filter(None, bidder[stat['key']])))
                    key = skill[0]['code']
                    if key not in stats['Skill']:
                        stats_key[key] = deepcopy(none_listed) if key == None else {'name': f"{skill[0]['description']}", 'value': 0}
                else:
                    if key not in stats[stat['statsKey']]:
                        stats_key[key] = deepcopy(none_listed) if key == None else {'name': f"{key}", 'value': 0}

                stats_key[key]['value'] += 1
                stats_sum[stat['statsKey']] += 1

            pydash.for_each(config, map_object)

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
        smart_str(u"Step Letter One"),
        smart_str(u"Step Letter Two"),
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
        smart_str(u"Updated"),
        smart_str(u"Notes"),
        smart_str(u"Shared with Bureau"),
    ])
    fields_info = {
        "name": None,
        "status": {"path": 'available_bidder_details.status', },
        "step_letter_one": {"path": 'available_bidder_details.step_letter_one', },
        "step_letter_two": {"path": 'available_bidder_details.step_letter_two', },
        "skills": {"default": "No Skills listed", "description_and_code": True},
        "grade": None,
        "ted": {"path": 'current_assignment.end_date', },
        "oc_bureau": {"path": 'available_bidder_details.oc_bureau', },
        "oc_reason": {"path": 'available_bidder_details.oc_reason', },
        "org": {"path": 'current_assignment.position.organization', },
        "city": {"path": 'current_assignment.position.post.location.city', },
        "state": {"path": 'current_assignment.position.post.location.state', },
        "country": {"path": 'current_assignment.position.post.location.country', },
        "updated_on": {"path": 'available_bidder_details.update_date', },
        "notes": {"path": 'available_bidder_details.comments', },
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

        # Removing time zone text to allow Maya to parse
        update_date, x, y = fields["updated_on"].partition('(')
        update_date = maya.parse(update_date).datetime().strftime('%m/%d/%Y')

        try:
            ted = maya.parse(fields["ted"]).datetime().strftime('%m/%d/%Y')
        except:
            ted = 'None listed'
        try:
            step_letter_one = maya.parse(fields["step_letter_one"]).datetime().strftime('%m/%d/%Y')
        except:
            step_letter_one = 'None listed'
        try:
            step_letter_two = maya.parse(fields["step_letter_two"]).datetime().strftime('%m/%d/%Y')
        except:
            step_letter_two = 'None listed'
        writer.writerow([
            fields["name"],
            fields["status"],
            fields["oc_bureau"],
            fields["oc_reason"],
            step_letter_one,
            step_letter_two,
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
            update_date,
            fields["notes"],
            mapBool[fields["is_shared"]],
        ])

    return response
