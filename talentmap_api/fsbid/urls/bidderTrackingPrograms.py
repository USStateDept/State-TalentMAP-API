from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import client as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidClientClassificationsListView.as_view(), name='FSBid-client_classifications'),
]

urlpatterns += router.urls