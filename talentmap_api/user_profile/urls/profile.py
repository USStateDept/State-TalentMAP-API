from django.conf.urls import url

from talentmap_api.user_profile import views
from talentmap_api.common.urls import get_retrieve, patch_update

urlpatterns = [
    url(r'^$', views.UserProfileView.as_view({**get_retrieve, **patch_update}), name='user_profile.UserProfile-detail'),
]
