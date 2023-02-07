from rest_framework import routers
from django.conf.urls import url

from talentmap_api.common.urls import get_list, get_retrieve
from talentmap_api.permission.views import user as views

router = routers.SimpleRouter()
router.register(r'', views.UserPermissionView, basename="permission.UserPermissionView")

urlpatterns = [
  url(r'^all/$', views.AllUserPermissionView.as_view({**get_list}), name='permissions.AllUserPermissionsView-list'),
  url(r'^(?P<pk>[0-9]+)/$', views.AllUserPermissionView.as_view({**get_retrieve}), name='permissions.AllUserPermissionsView-retrieve'),
]

urlpatterns += router.urls
