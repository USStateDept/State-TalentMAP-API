from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.OrganizationListView, base_name="organization.Organization")
router.register(r'^(?P<instance_id>[0-9]+)/history', views.HistoricalOrganizationView, base_name="organization.Organization-history")
router.register(r'group', views.OrganizationGroupListView, base_name="organization.OrganizationGroup")

urlpatterns = []

urlpatterns += router.urls
