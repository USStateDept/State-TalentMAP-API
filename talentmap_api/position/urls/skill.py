from rest_framework import routers

from talentmap_api.position import views

router = routers.SimpleRouter()
router.register(r'', views.SkillListView, base_name="position.Skill")

urlpatterns = []

urlpatterns += router.urls
