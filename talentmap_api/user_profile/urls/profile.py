from django.conf.urls import url

from talentmap_api.user_profile.views import profile as views
from talentmap_api.common.urls import get_retrieve, patch_update, get_list

urlpatterns = [
    url(r'^$', views.UserProfileView.as_view({**get_retrieve, **patch_update}), name='user_profile.UserProfile-detail'),
    url(r'^(?P<pk>[0-9]+)/$', views.UserPublicProfileView.as_view({**get_retrieve}), name='user_profile.UserPublicProfile-detail'),
]
