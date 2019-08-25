import pytest
import json

from model_mommy import mommy
from rest_framework import status

from talentmap_api.user_profile.models import SavedSearch
from talentmap_api.messaging.models import Notification


@pytest.fixture()
def test_saved_search_fixture(authorized_user):
    return mommy.make('user_profile.SavedSearch',
                      name="Test search",
                      owner=authorized_user.profile,
                      endpoint='/api/v1/position/',
                      filters={
                          "position_number__startswith": ["56"],
                      })


@pytest.mark.django_db()
def test_saved_search_create_no_endpoint(authorized_client, authorized_user):
    # Test posting with no endpoint
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
def test_saved_search_create_bad_endpoint(authorized_client, authorized_user):
    # Test a bad endpoint
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
            "endpoint": "/api/v1/asdf/"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
def test_saved_search_create_unfilterable_endpoint(authorized_client, authorized_user):
    # Test a bad endpoint
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
            "endpoint": "/api/v1/affff/"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
def test_saved_search_create_bad_filters(authorized_client, authorized_user):
    # Test a valid endpoint with bad filters
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
            "endpoint": "/api/v1/position/",
            "filters": {
                "asdf": ["05"]
            }
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
def test_saved_search_create_in_array_filters(authorized_client, authorized_user):
    # Test a valid endpoint with declared (i.e. manual) filters
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
            "endpoint": "/api/v1/position/",
            "filters": {
                "grade__code__in": ["05", "06"]
            }
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db()
def test_saved_search_create_in_string_filters(authorized_client, authorized_user):
    # Test a valid endpoint with declared (i.e. manual) filters
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
            "endpoint": "/api/v1/position/",
            "filters": {
                "post__in": "254,123"
            }
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db()
def test_saved_search_create_declared_filters(authorized_client, authorized_user):
    # Test a valid endpoint with declared (i.e. manual) filters
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
            "endpoint": "/api/v1/position/",
            "filters": {
                "q": ["german security"]
            }
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db()
def test_saved_search_create_valid_filters(authorized_client, authorized_user):
    # Test a valid endpoint with valid automatic filters
    response = authorized_client.post('/api/v1/searches/', data=json.dumps(
        {
            "name": "Banana search",
            "endpoint": "/api/v1/position/",
            "filters": {
                "position_number__startswith": ["56"],
                "title__in": ["SPECIAL AGENT", "OFFICE MANAGER"],
                "post__tour_of_duty__months__gt": ["6"]
            }
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db()
def test_saved_search_patch_bad_endpoint(authorized_client, authorized_user, test_saved_search_fixture):
    # Test patching a bad endpoint
    response = authorized_client.patch(f'/api/v1/searches/{test_saved_search_fixture.id}/', data=json.dumps(
        {
            "endpoint": "/api/v1/asdf/"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
def test_saved_search_patch_bad_filters(authorized_client, authorized_user, test_saved_search_fixture):
    # Test patching bad filters
    response = authorized_client.patch(f'/api/v1/searches/{test_saved_search_fixture.id}/', data=json.dumps(
        {
            "filters": {
                "asdf": ["05"]
            }
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
def test_saved_search_patch_valid_filters(authorized_client, authorized_user, test_saved_search_fixture):
    # Test a valid endpoint with valid filters and new endpoint
    response = authorized_client.patch(f'/api/v1/searches/{test_saved_search_fixture.id}/', data=json.dumps(
        {
            "endpoint": "/api/v1/organization/",
            "filters": {
                "code__startswith": ["56"],
                "long_description__in": ["OFF OF THE AMB-AT-LARGE FOR COUNTER-TERRORISM", "OFFICE MANAGER"],
                "bureau_organization__code__contains": ["6"]
            }
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_saved_search_delete(authorized_client, authorized_user, test_saved_search_fixture):
    response = authorized_client.delete(f'/api/v1/searches/{test_saved_search_fixture.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db(transaction=True)
def test_saved_search_counts(authorized_client, authorized_user):
    oms_contains = mommy.make('user_profile.SavedSearch',
                              name="Test search",
                              owner=authorized_user.profile,
                              endpoint='/api/v1/position/',
                              filters={
                                  "title__contains": "OMS",
                              })

    oms_exact = mommy.make('user_profile.SavedSearch',
                           name="Test search",
                           owner=authorized_user.profile,
                           endpoint='/api/v1/position/',
                           filters={
                               "title": "OMS",
                           })

    mommy.make('position.Position', title="OMS", _quantity=5)
    mommy.make('position.Position', title="OMS banana", _quantity=5)

    assert oms_contains.count == 0
    assert oms_exact.count == 0

    SavedSearch.update_counts_for_endpoint("/api/v1/position/")
    oms_contains.refresh_from_db()
    oms_exact.refresh_from_db()

    assert Notification.objects.filter(owner=authorized_user.profile).count() == 2
    assert oms_contains.count == 10
    assert oms_exact.count == 5

    mommy.make('position.Position', title="OMS", _quantity=5)

    SavedSearch.update_counts_for_endpoint()
    oms_contains.refresh_from_db()
    oms_exact.refresh_from_db()

    assert Notification.objects.filter(owner=authorized_user.profile).count() == 4
    assert oms_contains.count == 15
    assert oms_exact.count == 10