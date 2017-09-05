from rest_framework import routers

from talentmap_api.language import views

router = routers.SimpleRouter()
router.register(r'', views.LanguageProficiencyListView, base_name="language.Proficiency")

urlpatterns = []

urlpatterns += router.urls
