from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.LocationView, base_name="organization.Location")

urlpatterns = []

urlpatterns += router.urls
