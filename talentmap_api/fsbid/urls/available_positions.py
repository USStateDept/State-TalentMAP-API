from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import available_positions as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'', views.FSBidAvailablePositionsListView.as_view(), name="available-positions-FSBid-available-positions-actions"),
]

urlpatterns += router.urls
