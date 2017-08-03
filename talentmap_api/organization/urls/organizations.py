from rest_framework import routers
from django.conf.urls import url

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.OrganizationListView, base_name="organization.Organization")

urlpatterns = []

urlpatterns += router.urls
