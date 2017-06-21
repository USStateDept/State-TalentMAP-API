"""talentmap_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    url(r'^$', get_swagger_view(title='TalentMAP API')),
    url(r'^api/v1/language/', include('talentmap_api.language.urls')),
    url(r'^api/v1/position/', include('talentmap_api.position.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
