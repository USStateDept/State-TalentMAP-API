import pytest
import json

from django.contrib.auth.models import Group

from rest_framework import status

from model_mommy import mommy


@pytest.fixture
def feedback_editors_group():
    return Group.objects.create(name="feedback_editors")


@pytest.mark.django_db()
def test_feedback_user(authorized_client, authorized_user):
    response = authorized_client.post('/api/v1/feedback/', data=json.dumps(
        {
            "comments": "test",
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    response = authorized_client.post('/api/v1/feedback/', data=json.dumps(
        {
            "comments": "test2",
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    response = authorized_client.get('/api/v1/feedback/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2


@pytest.mark.django_db()
def test_feedback_admin(authorized_client, authorized_user, feedback_editors_group):
    new_user = mommy.make('auth.User').profile
    fbe_1 = mommy.make('feedback.FeedbackEntry', user=new_user)
    fbe_2 = mommy.make('feedback.FeedbackEntry', user=new_user)

    response = authorized_client.get('/api/v1/feedback/all/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    feedback_editors_group.user_set.add(authorized_user)

    response = authorized_client.get('/api/v1/feedback/all/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = authorized_client.get(f'/api/v1/feedback/all/{fbe_1.id}/')

    assert response.status_code == status.HTTP_200_OK

    response = authorized_client.delete(f'/api/v1/feedback/all/{fbe_1.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get('/api/v1/feedback/all/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
