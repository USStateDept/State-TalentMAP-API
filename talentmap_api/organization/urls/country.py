from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.CountryView, base_name="organization.Country")
router.register(r'^(?P<instance_id>[0-9]+)/history', views.HistoricalCountryView, base_name="organization.Country-history")

urlpatterns = []

urlpatterns += router.urls
