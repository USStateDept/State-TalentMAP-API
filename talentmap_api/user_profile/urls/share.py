from django.conf.urls import url

from talentmap_api.user_profile import views
from talentmap_api.common.urls import patch_update

urlpatterns = [
    url(r'^$', views.ShareView.as_view({'post': 'post'}), name='user_profile.Sharable-create'),
    url(r'^(?P<pk>[0-9]+)/$', views.ShareView.as_view(patch_update), name='user_profile.Sharable-patch'),
]
