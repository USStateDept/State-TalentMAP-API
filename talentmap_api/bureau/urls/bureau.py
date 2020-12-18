from django.conf.urls import url
from rest_framework import routers

from talentmap_api.bureau.views import available_bidders as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^availablebidders/$', views.AvailableBiddersListView.as_view(), name='bureau-available-bidders'),
    url(r'^availablebidders/export/$', views.AvailableBiddersCSVView.as_view(), name='bureau-export-available-bidders'),
]

urlpatterns += router.urls
