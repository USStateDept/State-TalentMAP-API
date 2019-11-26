from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import client as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^perdet_seq_num/$', views.FSBidCDOListView.as_view(), name='client.FSBid-cdo_list'),
]

urlpatterns += router.urls