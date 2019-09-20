from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.OrganizationListView, base_name="organization.Organization")
router.register(r'group', views.OrganizationGroupListView, base_name="organization.OrganizationGroup")

urlpatterns = []

urlpatterns += router.urls
