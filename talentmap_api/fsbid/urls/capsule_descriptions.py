from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import capsule_descriptions as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidCapsuleActionView.as_view(), name='FSBid-capsule'),
]

urlpatterns += router.urls
