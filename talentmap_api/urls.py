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
from rest_framework_expiring_authtoken import views as auth_views
from djangosaml2.views import echo_attributes
from talentmap_api.saml2.acs_patch import assertion_consumer_service

urlpatterns = [
    # Administration related resources
    url(r'^api/v1/homepage/', include('talentmap_api.administration.urls.homepage')),
    url(r'^api/v1/aboutpage/', include('talentmap_api.administration.urls.aboutpage')),

    # Position and position detail related resources
    url(r'^api/v1/position/', include('talentmap_api.position.urls.position')),
    url(r'^api/v1/skill/', include('talentmap_api.position.urls.skill')),
    url(r'^api/v1/grade/', include('talentmap_api.position.urls.grade')),
    url(r'^api/v1/capsule_description/', include('talentmap_api.position.urls.capsule_description')),

    # Bidding endpoints
    url(r'^api/v1/bid/', include('talentmap_api.bidding.urls.bid')),
    url(r'^api/v1/bidcycle/', include('talentmap_api.bidding.urls.bidcycle')),
    url(r'^api/v1/bidlist/', include('talentmap_api.bidding.urls.bidlist')),
    url(r'^api/v1/survey/', include('talentmap_api.bidding.urls.survey')),
    url(r'^api/v1/waiver/', include('talentmap_api.bidding.urls.waiver')),
    url(r'^api/v1/cycleposition/', include('talentmap_api.bidding.urls.cycleposition')),

    # FSBId
    url(r'^api/v1/fsbid/bidlist/', include('talentmap_api.fsbid.urls.bidlist')),
    url(r'^api/v1/fsbid/projected_vacancies/', include('talentmap_api.fsbid.urls.projected_vacancies')),
    url(r'^api/v1/fsbid/available_positions/', include('talentmap_api.fsbid.urls.available_positions')),
    url(r'^api/v1/fsbid/bid_seasons/', include('talentmap_api.fsbid.urls.bid_seasons')),

    # Projected Vacancies
    url(r'^api/v1/projected_vacancy/', include('talentmap_api.projected_vacancies.urls.projected_vacancies')),

    # Language and language related resources
    url(r'^api/v1/language/', include('talentmap_api.language.urls.languages')),
    url(r'^api/v1/language_proficiency/', include('talentmap_api.language.urls.proficiency')),
    url(r'^api/v1/language_qualification/', include('talentmap_api.language.urls.qualification')),

    # Organization and post related resources
    url(r'^api/v1/organization/', include('talentmap_api.organization.urls.organizations')),
    url(r'^api/v1/orgpost/', include('talentmap_api.organization.urls.post')),
    url(r'^api/v1/tour_of_duty/', include('talentmap_api.organization.urls.tour_of_duty')),
    url(r'^api/v1/location/', include('talentmap_api.organization.urls.location')),
    url(r'^api/v1/country/', include('talentmap_api.organization.urls.country')),

    # Permission resources
    url(r'^api/v1/permission/user/', include('talentmap_api.permission.urls.user')),
    url(r'^api/v1/permission/group/', include('talentmap_api.permission.urls.group')),

    # Profile and account related resources
    url(r'^api/v1/profile/', include('talentmap_api.user_profile.urls.profile')),
    url(r'^api/v1/share/', include('talentmap_api.messaging.urls.share')),
    url(r'^api/v1/searches/', include('talentmap_api.user_profile.urls.searches')),
    url(r'^api/v1/client/', include('talentmap_api.user_profile.urls.client')),

    # Messaging related resources
    url(r'^api/v1/notification/', include('talentmap_api.messaging.urls.notification')),
    url(r'^api/v1/task/', include('talentmap_api.messaging.urls.task')),

    # Glossary
    url(r'^api/v1/glossary/', include('talentmap_api.glossary.urls.glossary')),

    # Feedback
    url(r'^api/v1/feedback/', include('talentmap_api.feedback.urls.feedback')),

    # Data sync services
    url(r'^api/v1/data_sync/', include('talentmap_api.integrations.urls.data_sync_actions')),

    # Log viewing
    url(r'^api/v1/logs/', include('talentmap_api.log_viewer.urls.log_entry')),

    # Login statistics
    url(r'^api/v1/stats/', include('talentmap_api.stats.urls.logins'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Auth patterns
urlpatterns += [
    url(r'^api/v1/accounts/token/$', auth_views.obtain_expiring_auth_token),
    url(r'^api/v1/accounts/', include('rest_framework.urls')),
    url(r'^api/v1/accounts/token/view/', include('talentmap_api.common.tokens.urls')),
]

if settings.ENABLE_SAML2:  # pragma: no cover
    urlpatterns += [
        url(r'^saml2/acs/$', assertion_consumer_service, name='saml2_acs'),
        url(r'^saml2/', include('djangosaml2.urls')),
    ]
    if settings.DEBUG:
        urlpatterns += [
            url(r'^saml2-test/', echo_attributes),
        ]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^$', get_swagger_view(title='TalentMAP API')),
    ]
