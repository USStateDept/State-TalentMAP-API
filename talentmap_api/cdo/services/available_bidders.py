import logging
import csv

from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

from talentmap_api.cdo.models import AvailableBidders


logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_available_bidders(jwt_token):
    '''
    Returns Available Bidders list
    '''
    ab = AvailableBidders.objects.all()
    return ab.values('bidder_perdet', 'status', 'oc_reason', 'oc_bureau', 'comments', 'is_shared')


def get_available_bidders_csv(jwt_token):
    '''
    Returns csv format of Available Bidders list
    '''

    data = get_available_bidders(jwt_token)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=Available_Bidders_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Bidder Perdet"),
        smart_str(u"Status"),
        smart_str(u"OC Reason"),
        smart_str(u"OC Bureau"),
        smart_str(u"Comments"),
        smart_str(u"Shared with Bureau"),
    ])

    for record in data:
        writer.writerow([
            smart_str(record["bidder_perdet"]),
            smart_str("=\"%s\"" % record["status"]),
            smart_str("=\"%s\"" % record["oc_reason"]),
            smart_str("=\"%s\"" % record["oc_bureau"]),
            smart_str("=\"%s\"" % record["comments"]),
            smart_str("=\"%s\"" % record["is_shared"]),
        ])
    return response
