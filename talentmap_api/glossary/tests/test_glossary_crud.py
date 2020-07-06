import json
import pytest

from django.contrib.auth.models import Group

from rest_framework import status


@pytest.fixture
def glossary_editors_group():
    return Group.objects.create(name="glossary_editors")


@pytest.mark.django_db()
def test_glossary_crud(authorized_client, authorized_user, glossary_editors_group):
    response = authorized_client.post('/api/v1/glossary/', data=json.dumps(
        {
            "title": "test",
            "definition": "test_desc"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    glossary_editors_group.user_set.add(authorized_user)

    response = authorized_client.post('/api/v1/glossary/', data=json.dumps(
        {
            "title": "test",
            "definition": "test_desc"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    glossary_id = response.data["id"]

    response = authorized_client.patch(f'/api/v1/glossary/{glossary_id}/', data=json.dumps(
        {
            "link": "test_link"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
