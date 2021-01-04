import logging
import csv

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

from talentmap_api.cdo.models import AvailableBidders
import talentmap_api.bureau.services.available_bidders as bureau_services



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
        clients = bureau_services.get_available_bidders(jwt_token)
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
        smart_str(u"Grade"),
        smart_str(u"TED"),
        smart_str(u"Bidder Perdet"),
        smart_str(u"Status"),
        smart_str(u"OC Reason"),
        smart_str(u"OC Bureau"),
        smart_str(u"Comments"),
        smart_str(u"Shared with Bureau"),
    ])

    for record in data:
        writer.writerow([
            smart_str(record["name"]),
            smart_str(record["grade"]),
            smart_str(record["TED"]),
            smart_str(record["bidder_perdet"]),
            smart_str("=\"%s\"" % record["status"]),
            smart_str("=\"%s\"" % record["oc_reason"]),
            smart_str("=\"%s\"" % record["oc_bureau"]),
            smart_str("=\"%s\"" % record["comments"]),
            smart_str("=\"%s\"" % record["is_shared"]),
        ])
    return response
