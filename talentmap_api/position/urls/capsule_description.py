from django.conf.urls import url

from talentmap_api.position.views import capsule_description as views
from talentmap_api.common.urls import get_retrieve, get_list, patch_update

from rest_framework import routers

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.CapsuleDescriptionView.as_view({**get_retrieve, **patch_update}), name='position.CapsuleDescription-detail'),
    url(r'^$', views.CapsuleDescriptionView.as_view({**get_list}), name='position.CapsuleDescription-list-create'),
]

urlpatterns += router.urls
