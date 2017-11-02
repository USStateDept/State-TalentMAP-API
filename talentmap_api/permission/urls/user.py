from rest_framework import routers

from talentmap_api.permission.views import user as views

router = routers.SimpleRouter()
router.register(r'', views.UserPermissionView, base_name="permission.UserPermissionView")

urlpatterns = []

urlpatterns += router.urls
