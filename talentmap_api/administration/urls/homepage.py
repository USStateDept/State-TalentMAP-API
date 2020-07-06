from django.conf.urls import url
from rest_framework import routers
from talentmap_api.common.urls import get_retrieve, patch_update

from talentmap_api.administration.views import homepage as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^banner/$', views.HomepageBannerView.as_view({**get_retrieve, ** patch_update}), name='administration.Homepage-banner'),
]

urlpatterns += router.urls
