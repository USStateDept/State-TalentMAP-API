from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.TourOfDutyListView, base_name="organization.TourOfDuty")
router.register(r'^(?P<instance_id>[0-9]+)/history', views.HistoricalTourOfDutyView, base_name="organization.TourOfDuty-history")

urlpatterns = []

urlpatterns += router.urls
