from django.conf.urls import url
from rest_framework import routers

from talentmap_api.cdo.views import available_bidders as views

router = routers.SimpleRouter()

urlpatterns = [
    # 1 get list of Available Bidders
    url(r'^availablebidders/$', views.AvailableBiddersListView.as_view(), name='available-bidders'),
    # 2 get list of Ids, for properly rendering button text
    url(r'^availablebidders/ids/$', views.AvailableBiddersIdsListView.as_view(), name='available-bidders-ids'),
    # 3 Add and Remove to Available Bidders
    url(r'^(?P<pk>[0-9]+)/availablebidders/$', views.AvailableBiddersActionView.as_view(),
    name='update-available-bidders'),
    # 4 Export Available Bidders
    url(r'^availablebidders/export/$', views.AvailableBiddersCSVView.as_view(), name='export-available-bidders'),
]

urlpatterns += router.urls
