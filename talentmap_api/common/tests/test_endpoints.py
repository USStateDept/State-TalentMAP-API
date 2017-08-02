'''
This set of tests performs tests on all parameterized endpoints generically, any
more specific tests should be broken out into their own files.
'''

import pytest
import random

from model_mommy import mommy
from model_mommy.recipe import Recipe
from rest_framework import status

from django.apps import apps
from django.core.management import call_command

from talentmap_api.position.tests.mommy_recipes import favorite_position

parameterized_fields = "endpoint, model, recipe, retrievable"
parameterized_data = [
    # Position Endpoints
    ('/api/v1/position/', 'position.Position', 'talentmap_api.position.tests.position', True),
    ('/api/v1/skill/', 'position.Skill', 'talentmap_api.position.tests.skill', True),
    ('/api/v1/grade/', 'position.Grade', 'talentmap_api.position.tests.grade', True),
    ('/api/v1/position/favorites/', 'position.Position', favorite_position, False),

    # Language Endpoints
    ('/api/v1/language/', 'language.Language', 'talentmap_api.language.tests.language', True),
    ('/api/v1/language_proficiency/', 'language.Proficiency', 'talentmap_api.language.tests.proficiency', True),
    ('/api/v1/language_qualification/', 'language.Qualification', None, True),

    # Organization Endpoints
    ('/api/v1/organization/', 'organization.Organization', 'talentmap_api.organization.tests.orphaned_organization', True),
    ('/api/v1/post/', 'organization.Post', 'talentmap_api.organization.tests.post', True),
    ('/api/v1/tour_of_duty/', 'organization.TourOfDuty', 'talentmap_api.organization.tests.tour_of_duty', True),
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
    assert len(response.data) == apps.get_model(model).objects.count()
    assert len(response.data) == number


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(parameterized_fields, parameterized_data)
def test_endpoints_retrieve(authorized_client, authorized_user, endpoint, model, recipe, retrievable):
    # Skip any endpoints that don't support "retrieve" actions
    if not retrievable:
        return

    number = random.randint(5, 10)
    # Create a random amount of objects from the recipe, if it is given
    if recipe:
        mommy.make_recipe(recipe, _quantity=number)
    elif model:
        mommy.make(model, _quantity=number)

    # Check that each item is retrievable
    for id in apps.get_model(model).objects.values_list('id', flat=True):
        response = authorized_client.get(f"{endpoint}{id}/")
        assert response.status_code == status.HTTP_200_OK
