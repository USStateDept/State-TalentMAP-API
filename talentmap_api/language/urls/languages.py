from rest_framework import routers
from django.conf.urls import url

from talentmap_api.language import views

router = routers.SimpleRouter()
router.register(r'', views.LanguageListView, base_name="language.Language")

urlpatterns = []

urlpatterns += router.urls
