from django.conf.urls import url

from talentmap_api.user_profile import views
from talentmap_api.common.urls import get_retrieve, patch_update, get_list

urlpatterns = [
    url(r'^$', views.UserProfileView.as_view({**get_retrieve, **patch_update}), name='user_profile.UserProfile-detail'),
    url(r'^assignments/$', views.UserAssignmentHistoryView.as_view({**get_list}), name='user_profile.UserProfile-assignment-list')
]
