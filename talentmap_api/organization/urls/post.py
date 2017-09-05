from rest_framework import routers

from talentmap_api.organization import views

router = routers.SimpleRouter()
router.register(r'', views.PostListView, base_name="organization.Post")

urlpatterns = []

urlpatterns += router.urls
