from django.conf.urls import url
from rest_framework import routers

from talentmap_api.bureau.views import bidder_rankings as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.BureauBiddersRankings.as_view(), name='bureau-bidder-rankings'),
]

urlpatterns += router.urls
