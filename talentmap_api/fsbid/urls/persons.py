from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import persons as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', views.FSBidPersonsView.as_view(), name="FSBid-persons"),
]

urlpatterns += router.urls
