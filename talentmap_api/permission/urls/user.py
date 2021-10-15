from rest_framework import routers
from django.conf.urls import url

from talentmap_api.common.urls import get_list
from talentmap_api.permission.views import user as views

router = routers.SimpleRouter()
router.register(r'', views.UserPermissionView, basename="permission.UserPermissionView")

urlpatterns = [
  url(r'^all/$', views.AllUserPermissionView.as_view({**get_list}), name='permissions.AllUserPermissionsView-list'),
]

urlpatterns += router.urls
