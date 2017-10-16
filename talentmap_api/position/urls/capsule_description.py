from django.conf.urls import url

from talentmap_api.position.views import capsule_description as views
from talentmap_api.common.urls import get_retrieve, get_list, delete_destroy, patch_update, post_create

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.CapsuleDescriptionView.as_view({**get_retrieve, **delete_destroy, **patch_update}), name='position.CapsuleDescription-detail'),
    url(r'^$', views.CapsuleDescriptionView.as_view({**get_list, **post_create}), name='position.CapsuleDescription-list-create'),
]
