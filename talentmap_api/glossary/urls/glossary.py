from rest_framework import routers

from talentmap_api.glossary.views import glossary as views

router = routers.SimpleRouter()
router.register(r'', views.GlossaryView, base_name="glossary.GlossaryEntry")

urlpatterns = []

urlpatterns += router.urls
