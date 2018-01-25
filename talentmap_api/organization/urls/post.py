from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.PostListView, base_name="organization.Post")
router.register(r'^(?P<instance_id>[0-9]+)/history', views.HistoricalPostView, base_name="organization.Post-history")

urlpatterns = []

urlpatterns += router.urls
