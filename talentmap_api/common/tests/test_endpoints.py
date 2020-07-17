'''
This set of tests performs tests on all parameterized endpoints generically, any
more specific tests should be broken out into their own files.
'''

import pytest
import random

from model_mommy import mommy
from rest_framework import status

from django.apps import apps

from talentmap_api.bidding.tests.mommy_recipes import tz_aware_bidcycle
from talentmap_api.position.tests.mommy_recipes import highlighted_position, cycle_position
from talentmap_api.user_profile.tests.mommy_recipes import owned_saved_search
from talentmap_api.messaging.tests.mommy_recipes import owned_notification

parameterized_fields = "endpoint, model, recipe, retrievable"
parameterized_data = [
    # Bidcycle Endpoints
    ('/api/v1/bidcycle/', 'bidding.BidCycle', None, True),
    ('/api/v1/bidcycle/statistics/', 'bidding.BidCycle', tz_aware_bidcycle, False),
    
    # Position Endpoints
    ('/api/v1/position/', 'bidding.CyclePosition', cycle_position, False),
    ('/api/v1/skill/', 'position.Skill', 'talentmap_api.position.tests.skill', True),
    ('/api/v1/skill/cone/', 'position.SkillCone', None, True),
    ('/api/v1/grade/', 'position.Grade', 'talentmap_api.position.tests.grade', True),
    ('/api/v1/position/highlighted/', 'position.Position', highlighted_position, False),
    ('/api/v1/capsule_description/', 'position.CapsuleDescription', None, True),
    ('/api/v1/position/classification/', 'position.Classification', None, True),

    # Language Endpoints
    ('/api/v1/language/', 'language.Language', 'talentmap_api.language.tests.language', True),
    ('/api/v1/language_proficiency/', 'language.Proficiency', 'talentmap_api.language.tests.proficiency', True),
    ('/api/v1/language_qualification/', 'language.Qualification', None, True),

    # Organization Endpoints
    ('/api/v1/organization/', 'organization.Organization', 'talentmap_api.organization.tests.orphaned_organization', True),
    ('/api/v1/organization/group/', 'organization.OrganizationGroup', None, True),
    ('/api/v1/orgpost/', 'organization.Post', 'talentmap_api.organization.tests.post', True),
    ('/api/v1/tour_of_duty/', 'organization.TourOfDuty', 'talentmap_api.organization.tests.tour_of_duty', True),
    ('/api/v1/location/', 'organization.Location', 'talentmap_api.organization.tests.location', True),
    ('/api/v1/country/', 'organization.Country', 'talentmap_api.organization.tests.country', True),

    # Permission Endpoints
    ('/api/v1/permission/group/', 'auth.Group', None, True),

    # Saved Searches
    ('/api/v1/searches/', 'user_profile.SavedSearch', owned_saved_search, True),

    # Messaging Endpoints
    ('/api/v1/notification/', 'messaging.Notification', owned_notification, True),

    # Glossary
    ('/api/v1/glossary/', 'glossary.GlossaryEntry', None, True),
]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(parameterized_fields, parameterized_data)
def test_endpoints_list(authorized_client, authorized_user, endpoint, model, recipe, retrievable):
    number = random.randint(5, 10)
    # Create a random amount of objects from the recipe, if it is given
    if recipe:
        if callable(recipe):
            for i in range(0, number):
                recipe()
        else:
            mommy.make_recipe(recipe, _quantity=number)
    elif model:
        mommy.make(model, _quantity=number)

    response = authorized_client.get(endpoint)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == apps.get_model(model).objects.count()
    assert len(response.data["results"]) == number


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(parameterized_fields, parameterized_data)
def test_endpoints_retrieve(authorized_client, authorized_user, endpoint, model, recipe, retrievable):
    # Skip any endpoints that don't support "retrieve" actions
    if not retrievable:
        return

    number = random.randint(5, 10)
    # Create a random amount of objects from the recipe, if it is given
    if recipe:
        if callable(recipe):
            for i in range(0, number):
                recipe()
        else:
            mommy.make_recipe(recipe, _quantity=number)
    elif model:
        mommy.make(model, _quantity=number)

    # Check that each item is retrievable
    for id in apps.get_model(model).objects.values_list('id', flat=True):
        response = authorized_client.get(f"{endpoint}{id}/")
        assert response.status_code == status.HTTP_200_OK
