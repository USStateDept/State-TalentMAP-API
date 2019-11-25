from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import client as views

# Need help fixing the router

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^perdet_seq_num/$', views.FSBidClientActionView.as_view(), name='client.FSBid-perdet_seq_num-actions'),
]

urlpatterns += router.urls