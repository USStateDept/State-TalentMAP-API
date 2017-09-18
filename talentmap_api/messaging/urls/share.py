from django.conf.urls import url

from talentmap_api.messaging import views
from talentmap_api.common.urls import patch_update

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.ShareView.as_view(), name='messaging.Sharable-patch'),
    url(r'^$', views.ShareView.as_view(), name='messaging.Sharable-create'),
]
