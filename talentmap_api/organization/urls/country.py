from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.CountryView, base_name="organization.Country")

urlpatterns = []

urlpatterns += router.urls
