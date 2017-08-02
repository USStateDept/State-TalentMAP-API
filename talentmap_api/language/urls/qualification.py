from rest_framework import routers
from django.conf.urls import url

from talentmap_api.language import views

router = routers.SimpleRouter()
router.register(r'', views.LanguageQualificationListView, base_name="language.Qualification")

urlpatterns = []

urlpatterns += router.urls
