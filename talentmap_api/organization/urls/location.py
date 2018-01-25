from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.LocationView, base_name="organization.Location")
router.register(r'^(?P<instance_id>[0-9]+)/history', views.HistoricalLocationView, base_name="organization.Location-history")

urlpatterns = []

urlpatterns += router.urls
