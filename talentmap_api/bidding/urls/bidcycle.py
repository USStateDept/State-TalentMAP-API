from django.conf.urls import url

from talentmap_api.bidding.views import bidcycle as views
from talentmap_api.common.urls import get_retrieve, patch_update, post_create, get_list

urlpatterns = [
    url(r'^$', views.BidCycleView.as_view({**get_list, **post_create})),
    url(r'^(?P<pk>[0-9]+)/$', views.BidCycleView.as_view({**get_retrieve, **patch_update}), name="bidding.BidCycle-details"),
    url(r'^(?P<pk>[0-9]+)/position/(?P<pos_id>[0-9]+)/$', views.BidCyclePositionActionView.as_view(), name='bidding.BidCycle-position-actions'),
    url(r'^(?P<pk>[0-9]+)/positions/$', views.BidCycleListPositionView.as_view(get_list), name="bidding.BidCycle-list-positions"),
    url(r'^(?P<pk>[0-9]+)/position/batch/(?P<saved_search_id>[0-9]+)/$', views.BidCycleBatchPositionActionView.as_view(), name="bidding.BidCycle-position-batch")
]
