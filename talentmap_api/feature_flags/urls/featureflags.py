from django.conf.urls import url
from rest_framework import routers
from talentmap_api.common.urls import get_retrieve, post_create

from talentmap_api.feature_flags.views import featureflags as views

router = routers.SimpleRouter()

urlpatterns = [
  url(r'^$', views.FeatureFlagsView.as_view({**get_retrieve, 'post': 'perform_create'}), name='featureflags'),
]

urlpatterns += router.urls
