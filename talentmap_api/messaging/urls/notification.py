from rest_framework import routers
from django.conf.urls import url

from talentmap_api.messaging import views
from talentmap_api.common.urls import get_retrieve, get_list, delete_destroy, patch_update, post_create

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.NotificationView.as_view({**get_retrieve, **delete_destroy, **patch_update}), name='messaging.NotificationView-detail'),
    url(r'^$', views.NotificationView.as_view({**get_list}), name='messaging.NotificationView-list-create'),
]
