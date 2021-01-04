from django.conf.urls import url
from rest_framework import routers

from talentmap_api.cdo.views import available_bidders as views
from talentmap_api.common.urls import post_create, patch_update, delete_destroy

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/availablebidder/$', views.AvailableBidderView.as_view(), name='available-bidder'),
    url(r'^availablebidders/$', views.AvailableBiddersListView.as_view(), name='available-bidders'),
    url(r'^availablebidders/ids/$', views.AvailableBiddersIdsListView.as_view(), name='available-bidders-ids'),
    url(r'^(?P<pk>[0-9]+)/availablebidders/$', views.AvailableBiddersActionView.as_view({'put': 'put', 'patch': 'patch', 'delete': 'delete'}),
        name='update-available-bidders'),
    url(r'^availablebidders/export/$', views.AvailableBiddersCSVView.as_view(), name='export-available-bidders'),
]

urlpatterns += router.urls
