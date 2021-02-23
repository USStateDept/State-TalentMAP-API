import logging
import csv
import maya

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

from talentmap_api.cdo.models import AvailableBidders
import talentmap_api.bureau.services.available_bidders as bureau_services
import talentmap_api.fsbid.services.client as client_services



logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders(jwt_token):
    '''
    Returns Available Bidders list
    '''
    ab = AvailableBidders.objects.all()
    stats = {
        'UA': 0,
        'IT': 0,
        'OC': 0,
        'LWOP': 0,
    }
    if len(ab) > 0:
        results = ab.values('bidder_perdet', 'status', 'oc_reason', 'oc_bureau', 'comments', 'is_shared')
        # TEMPORARY while we have a better solution merge ab with clients
        clients = bureau_services.get_available_bidders(jwt_token, True)
        ab_clients = []
        for bidder in results:
            for index, client in enumerate(clients):
                if int(bidder["bidder_perdet"]) == int(client["perdet_seq_number"]):
                    ab_clients.append({**bidder,
                                       **{'name': client['name'],
                                          'grade': client['grade'],
                                          'skills': client['skills'],
                                          'TED': client['current_assignment']['end_date'],
                                          'post': client['current_assignment']['position']['post'],
                                          }})
                    # i'm so efficient >.<
                    clients.pop(index)

        # get stats for status field
        for stat in ab.values('status'):
            if stat['status'] is not '':
                stats[stat['status']] += 1

        return {"count": len(results), "results": ab_clients, "stats": stats}
    else:
        return {"count": 0, "results": [], "stats": stats}


def get_available_bidders_csv(jwt_token):
    '''
    Returns csv format of Available Bidders list
    '''
    data = get_available_bidders(jwt_token)['results']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=Available_Bidders_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Status"),
        smart_str(u"Skills"),
        smart_str(u"Grade"),
        smart_str(u"TED"),
        smart_str(u"Post"),
        smart_str(u"OC Bureau"),
        smart_str(u"OC Reason"),
        smart_str(u"CDO"),
        smart_str(u"Comments"),
        smart_str(u"Shared with Bureau"),
    ])
    # TODO: cdo not currently coming through
    for record in data:
        fields = {
            "name": None,
            "status": None,
            "skills": None,
            "grade": None,
            "ted": None,
            "post": None,
            "oc_bureau": None,
            "oc_reason": None,
            "cdo": None,
            "comments": None,
            "is_shared": None,
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
                        fields[f] = maya.parse(record["TED"]).datetime().strftime('%m/%d/%Y')
                    elif f is "post":
                        fields[f] = record["post"]["location"]["country"]
                    else:
                        fields[f] = record[f]
                except:
                    fields[f] = "None listed"
                finally:
                    if fields[f] is "":
                        fields[f] = "None listed"

        writer.writerow([
            fields["name"],
            fields["status"],
            fields["skills"],
            smart_str("=\"%s\"" % fields["grade"]),
            fields["ted"],
            fields["post"],
            fields["oc_bureau"],
            fields["oc_reason"],
            fields["cdo"],
            fields["comments"],
            fields["is_shared"],
        ])
    return response
