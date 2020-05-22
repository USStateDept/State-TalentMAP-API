from django.conf.urls import url

from talentmap_api.user_profile.views import searches as views
from talentmap_api.common.urls import get_retrieve, get_list, delete_destroy, patch_update, post_create

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.SavedSearchView.as_view({**get_retrieve, **delete_destroy, **patch_update}), name='user_profile.SavedSearch-detail'),
    url(r'^$', views.SavedSearchView.as_view({**get_list, **post_create}), name='user_profile.SavedSearch-list-create'),
    url(r'^listcount/$', views.SavedSearchListCountView.as_view(), name='user_profile.SavedSearchList-count'),
]
