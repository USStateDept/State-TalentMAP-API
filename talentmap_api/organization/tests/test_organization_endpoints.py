import pytest

from model_mommy import mommy
from rest_framework import status

from talentmap_api.organization.models import Organization


# Might move this fixture to a session fixture if we end up needing languages elsewhere
@pytest.fixture
def test_organization_endpoints_fixture():
    cheese_bureau = mommy.make(Organization, code="cheese", short_description="", long_description="Bureau of Cheese Imports", is_bureau=True)
    mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization', is_bureau=False, bureau_organization=cheese_bureau, _quantity=2)
    mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization', is_bureau=False, parent_organization=cheese_bureau, _quantity=2)

    # Some organizations who don't have linked bureau/parent but do have codes
    mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization', is_bureau=False, _parent_bureau_code=cheese_bureau.code, _quantity=2)
    mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization', is_bureau=False, _parent_organization_code=cheese_bureau.code, _quantity=2)


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_organization_endpoints_fixture")
def test_organization_list(client):
    response = client.get('/api/v1/organization/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == Organization.objects.count()


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_organization_endpoints_fixture")
def test_organization_list_clear_parent_names(client):
    response = client.get('/api/v1/organization/?is_bureau=false')

    assert response.status_code == status.HTTP_200_OK

    for item in response.data["results"]:
        assert (item["bureau_organization"] == "() Bureau of Cheese Imports" or
                item["bureau_organization"] == "cheese" or
                item["parent_organization"] == "() Bureau of Cheese Imports" or
                item["parent_organization"] == "cheese")


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_organization_endpoints_fixture")
def test_organization_filters(client):
    response = client.get('/api/v1/organization/?is_bureau=true')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["long_description"] == "Bureau of Cheese Imports"
