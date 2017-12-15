from django.conf.urls import url
from rest_framework import routers

from talentmap_api.bidding.views import bidlist as views

router = routers.SimpleRouter()
router.register(r'', views.BidListView, base_name="bidding.BidList")

urlpatterns = [
    url(r'^position/(?P<pk>[0-9]+)/$', views.BidListPositionActionView.as_view(), name='bidding.Bid-position-actions'),
]

urlpatterns += router.urls
