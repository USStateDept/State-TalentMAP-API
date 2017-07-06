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

parameterized_fields = "endpoint, model, recipe"
parameterized_data = [
    # Position Endpoints
    ('/api/v1/position/', 'position.Position', 'talentmap_api.position.tests.position'),
    ('/api/v1/position/skills/', 'position.Skill', 'talentmap_api.position.tests.skill'),
    ('/api/v1/position/grades/', 'position.Grade', 'talentmap_api.position.tests.grade'),

    # Language Endpoints
    ('/api/v1/language/', 'language.Language', 'talentmap_api.language.tests.language'),
    ('/api/v1/language/proficiencies/', 'language.Proficiency', 'talentmap_api.language.tests.proficiency'),
    ('/api/v1/language/qualifications/', 'language.Qualification', None),

    # Organization Endpoints
    ('/api/v1/organization/', 'organization.Organization', 'talentmap_api.organization.tests.orphaned_organization'),
    ('/api/v1/organization/posts/', 'organization.Post', 'talentmap_api.organization.tests.post'),
    ('/api/v1/organization/tod/', 'organization.TourOfDuty', 'talentmap_api.organization.tests.tour_of_duty'),
]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(parameterized_fields, parameterized_data)
def test_endpoints_list(client, endpoint, model, recipe):
    number = random.randint(5, 10)
    # Create a random amount of objects from the recipe, if it is given
    if recipe:
        mommy.make_recipe(recipe, _quantity=number)
    elif model:
        mommy.make(model, _quantity=number)

    response = client.get(endpoint)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == apps.get_model(model).objects.count()
    assert len(response.data) == number


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(parameterized_fields, parameterized_data)
def test_endpoints_retrieve(client, endpoint, model, recipe):
    number = random.randint(5, 10)
    # Create a random amount of objects from the recipe, if it is given
    if recipe:
        mommy.make_recipe(recipe, _quantity=number)
    elif model:
        mommy.make(model, _quantity=number)

    # Check that each item is retrievable
    for id in apps.get_model(model).objects.values_list('id', flat=True):
        response = client.get(f"{endpoint}{id}/")
        assert response.status_code == status.HTTP_200_OK
