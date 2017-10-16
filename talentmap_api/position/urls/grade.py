from rest_framework import routers

from talentmap_api.position.views import grade as views

router = routers.SimpleRouter()
router.register(r'', views.GradeListView, base_name="position.Grade")

urlpatterns = []

urlpatterns += router.urls
