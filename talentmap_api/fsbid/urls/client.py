from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import client as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidClientListView.as_view(), name='FSBid-client_list'),
]

urlpatterns += router.urls