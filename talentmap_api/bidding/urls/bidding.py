from django.conf.urls import url
from rest_framework import routers

from talentmap_api.bidding.views import bidhandshake as views
from talentmap_api.common.urls import get_list, get_retrieve, patch_update

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^handshake/bureau/(?P<pk>[0-9]+)/(?P<cp_id>[0-9]+)/$', views.BidHandshakeBureauActionView.as_view({'put': 'put', 'delete': 'delete'}), name='bidding.CyclePosition-designation'),
    url(r'^handshake/cdo/(?P<pk>[0-9]+)/(?P<cp_id>[0-9]+)/$', views.BidHandshakeCdoActionView.as_view({'put': 'put', 'delete': 'delete'}), name='bidding.CyclePosition-designation'),
    url(r'^handshake/bidder/(?P<cp_id>[0-9]+)/$', views.BidHandshakeBidderActionView.as_view({'put': 'put', 'delete': 'delete'}), name='bidding.CyclePosition-designation'),
]


urlpatterns += router.urls
