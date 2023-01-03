from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import capsule_descriptions as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidCapsuleView.as_view(), name='FSBid-capsule'),
    url(r'^(?P<pk>[0-9]+)/update$', views.FSBidCapsuleActionView.as_view(), name='FSBid-update-capsule'),
]

urlpatterns += router.urls
