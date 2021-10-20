from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bureau as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/bids/$', views.FSBidBureauPositionBidsView.as_view(), name='bureau-positions-FSBid-bureau-position-bids'),
    url(r'^(?P<pk>[0-9]+)/bids/export/$', views.FSBidBureauPositionBidsCSVView.as_view(), name='bureau-positions-FSBid-bureau-position-bids-export'),
    url(r'^export/$', views.FSBidBureauPositionsCSVView.as_view(), name='bureau-positions-FSBid-bureau-positions-actions'),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidBureauPositionView.as_view(), name='bureau-positions-FSBid-bureau-position'),
    url(r'^$', views.FSBidBureauPositionsListView.as_view(), name='bureau-positions-FSBid-bureau-positions-actions'),
]

urlpatterns += router.urls
