from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import bid_seasons as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidBidSeasonsListView.as_view(), name="bid-seasons-FSBid-bid-seasons-actions"),
]

urlpatterns += router.urls
