import pytest
import json

from talentmap_api.messaging.models import Task

from model_mommy import mommy
from rest_framework import status


@pytest.fixture
def test_task_fixture(authorized_user):
    mommy.make(Task, id=1, owner=authorized_user.profile, content="banana", tags=["fruit", "potassium"])


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_task_fixture")
def test_task_tag_filters(authorized_client, authorized_user):
    mommy.make(Task, id=2, owner=authorized_user.profile, content="apple", tags=["fruit"])
    mommy.make(Task, id=3, owner=authorized_user.profile, content="vitamin pill", tags=["potassium"])
    mommy.make(Task, id=4, owner=authorized_user.profile, content="cardboard")

    response = authorized_client.get('/api/v1/task/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 4

    response = authorized_client.get('/api/v1/task/?tags=fruit')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = authorized_client.get('/api/v1/task/?tags=potassium')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = authorized_client.get('/api/v1/task/?tags=fruit,potassium')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/task/?tags=potassium,fruit')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/task/?tags__overlap=fruit,potassium')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_task_fixture")
def test_task_update(authorized_client, authorized_user):
    assert Task.objects.count() == 1
    task = Task.objects.get(id=1)
    assert not task.priority == 1

    response = authorized_client.patch('/api/v1/task/1/', data=json.dumps(
        {
            "priority": 1
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    task.refresh_from_db()
    assert task.priority == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_task_fixture")
def test_task_delete(authorized_client, authorized_user):
    assert Task.objects.count() == 1

    response = authorized_client.delete('/api/v1/task/1/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Task.objects.count() == 0
