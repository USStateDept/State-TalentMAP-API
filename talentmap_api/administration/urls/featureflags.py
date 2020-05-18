from django.conf.urls import url
from rest_framework import routers
from talentmap_api.common.urls import get_retrieve, patch_update

from talentmap_api.administration.views import featureflags as views

router = routers.SimpleRouter()

urlpatterns = [
  url(r'^$', views.FeatureFlagsView.as_view({**get_retrieve, ** patch_update}), name='administration.featureflags'),
]

urlpatterns += router.urls
