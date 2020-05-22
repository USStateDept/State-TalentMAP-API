from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import available_positions as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^export/$', views.FSBidAvailablePositionsCSVView.as_view(), name="available-positions-FSBid-available-positions-actions"),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidAvailablePositionView.as_view(), name='available-positions-FSBid-available-position'),
    url(r'^archived/(?P<pk>[0-9]+)/$', views.FSBidUnavailablePositionView.as_view(), name='available-positions-FSBid-unavailable-position'),
    url(r'^(?P<pk>[0-9]+)/similar/$', views.FSBidAvailablePositionsSimilarView.as_view(), name='available-positions-FSBid-available-positions-similar'),
    url(r'^tandem/$', views.FSBidAvailablePositionsTandemListView.as_view(), name="available-positions-FSBid-available-positions-actions"),
    url(r'^tandem/export/$', views.FSBidAvailablePositionsTandemCSVView.as_view(), name="available-positions-FSBid-available-positions-actions"),
    url(r'^$', views.FSBidAvailablePositionsListView.as_view(), name="available-positions-FSBid-available-positions-actions"),
]

urlpatterns += router.urls
