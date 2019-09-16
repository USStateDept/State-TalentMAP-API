from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.TourOfDutyListView, base_name="organization.TourOfDuty")

urlpatterns = []

urlpatterns += router.urls
