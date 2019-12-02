from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import cdo as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidCDOListView.as_view(), name='FSBid-cdo_list'),
]

urlpatterns += router.urls