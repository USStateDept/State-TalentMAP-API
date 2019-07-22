from django.conf.urls import url
from rest_framework import routers

from talentmap_api.bidding.views import cycleposition as views
from talentmap_api.common.urls import get_list, get_retrieve

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.CyclePositionListView.as_view(get_list), name='bidding.CyclePosition-list'),
    url(r'^highlighted/$', views.CyclePositionHighlightListView.as_view(get_list), name='view-highlighted-cyclepositions'),
    url(r'^favorites/$', views.CyclePositionFavoriteListView.as_view(get_list), name='view-favorite-cyclepositions'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.CyclePositionFavoriteActionView.as_view(), name='bidding.CyclePosition-favorite'),
    url(r'^(?P<pk>[0-9]+)/$', views.CyclePositionListView.as_view({**get_retrieve}), name='bidding.CyclePosition-detail'),
    url(r'^(?P<pk>[0-9]+)/bids/$', views.CyclePositionBidListView.as_view(get_list), name='bidding.CyclePosition-bids'),
    url(r'^(?P<pk>[0-9]+)/similar/$', views.CyclePositionSimilarView.as_view(get_list), name='bidding.CyclePosition-similar'),
]   

urlpatterns += router.urls
