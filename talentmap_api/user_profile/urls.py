from django.conf.urls import url

from talentmap_api.user_profile import views
from talentmap_api.common.urls import get_list, get_retrieve

urlpatterns = [
    url(r'^$', views.UserProfileView.as_view(get_retrieve), name='view-profile'),
    url(r'^favorites/$', views.UserFavoritePositionView.as_view(), name='view-profile-favorites')
]
