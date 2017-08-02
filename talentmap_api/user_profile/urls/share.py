from rest_framework import routers
from django.conf.urls import url

from talentmap_api.user_profile import views
from talentmap_api.common.urls import get_retrieve, get_list, delete_destroy, patch_update, post_create

urlpatterns = [
    url(r'^$', views.ShareView.as_view({'post': 'post'}), name='user_profile.Sharable-create'),
    url(r'^(?P<pk>[0-9]+)/$', views.ShareView.as_view(patch_update), name='user_profile.Sharable-patch'),
]
