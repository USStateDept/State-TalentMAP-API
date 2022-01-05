from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import classifications as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidClassificationsView.as_view(), name='FSBid-classifications'),
]

urlpatterns += router.urls
