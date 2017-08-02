from rest_framework import routers
from django.conf.urls import url

from talentmap_api.user_profile import views
from talentmap_api.common.urls import get_retrieve, get_list, delete_destroy, patch_update, post_create

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.SavedSearchView.as_view(get_retrieve), name='user_profile.SavedSearch-detail'),
    url(r'^(?P<pk>[0-9]+)/$', views.SavedSearchView.as_view(delete_destroy), name='user_profile.SavedSearch-delete'),
    url(r'^(?P<pk>[0-9]+)/$', views.SavedSearchView.as_view(patch_update), name='user_profile.SavedSearch-patch'),
    url(r'^$', views.SavedSearchView.as_view(get_list), name='user_profile.SavedSearch-list'),
    url(r'^$', views.SavedSearchView.as_view(post_create), name='user_profile.SavedSearch-create'),
]
