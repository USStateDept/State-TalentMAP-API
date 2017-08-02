from django.conf.urls import url

from talentmap_api.user_profile import views
from talentmap_api.common.urls import get_list, get_retrieve

urlpatterns = [
    url(r'^$', views.UserProfileView.as_view({**get_retrieve, "patch": "partial_update"}), name='view-profile'),
    url(r'^share/$', views.ShareView.as_view({"post": "post"}), name='create-share'),
    url(r'^share/(?P<pk>[0-9]+)/$', views.ShareView.as_view({"patch": "partial_update"}), name='update-share')
]
