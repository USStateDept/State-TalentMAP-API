from rest_framework import routers
from django.conf.urls import url

from talentmap_api.permission.views import group as views

router = routers.SimpleRouter()
router.register(r'', views.PermissionGroupView, basename="permission.PermissionGroupView")

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/user/(?P<user_id>[0-9]+)/$', views.PermissionGroupControls.as_view(), name='permissions.PermissionGroupControls-membership-actions'),
]

urlpatterns += router.urls
