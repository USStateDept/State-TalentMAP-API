from django.conf.urls import url

from talentmap_api.messaging import views
from talentmap_api.common.urls import get_retrieve, get_list, delete_destroy, patch_update

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.TaskView.as_view({**get_retrieve, **delete_destroy, **patch_update}), name='messaging.TaskView-detail'),
    url(r'^$', views.TaskView.as_view({**get_list}), name='messaging.TaskView-list-create'),
]
