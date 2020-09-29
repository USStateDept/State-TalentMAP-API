import json
import pytest

from model_mommy import mommy
from rest_framework import status

from talentmap_api.user_profile.models import SavedSearch
from talentmap_api.messaging.models import Notification


@pytest.fixture()
def test_saved_search_fixture(authorized_user):
    return mommy.make('user_profile.SavedSearch',
                      name="Test search",
                      owner=authorized_user.profile,
                      endpoint='/api/v1/fsbid/available_positions/',
                      filters={
                          "q": "german",
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
def test_saved_search_patch_bad_endpoint(authorized_client, authorized_user, test_saved_search_fixture):
    # Test patching a bad endpoint
    response = authorized_client.patch(f'/api/v1/searches/{test_saved_search_fixture.id}/', data=json.dumps(
        {
            "endpoint": "/api/v1/asdf/"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# TODO - add back in. Failing after oracle migration (had to change endpoint)
#@pytest.mark.django_db()
#def test_saved_search_patch_valid_filters(authorized_client, authorized_user, test_saved_search_fixture):
#    # Test a valid endpoint with valid filters and new endpoint
#    response = authorized_client.patch(f'/api/v1/searches/{test_saved_search_fixture.id}/', data=json.dumps(
#        {
#            "endpoint": "/api/v1/fsbid/available_positions/",
#            "filters": {
#                "q": "german"
#            }
#        }
#    ), content_type='application/json', HTTP_JWT='test')
#
#    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_saved_search_delete(authorized_client, authorized_user, test_saved_search_fixture):
    response = authorized_client.delete(f'/api/v1/searches/{test_saved_search_fixture.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
