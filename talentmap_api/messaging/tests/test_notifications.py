import json

import pytest
from model_mommy import mommy
from rest_framework import status

from talentmap_api.messaging.models import Notification

@pytest.fixture
def test_notification_fixture(authorized_user):
    mommy.make(Notification, id=1, owner=authorized_user.profile, message="banana", tags=["fruit", "potassium"])


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_notification_fixture")
def test_notification_tag_filters(authorized_client, authorized_user):
    mommy.make(Notification, id=2, owner=authorized_user.profile, message="apple", tags=["fruit"])
    mommy.make(Notification, id=3, owner=authorized_user.profile, message="vitamin pill", tags=["potassium"])
    mommy.make(Notification, id=4, owner=authorized_user.profile, message="cardboard")

    response = authorized_client.get('/api/v1/notification/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 4


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_notification_fixture")
def test_notification_update(authorized_client, authorized_user):
    assert Notification.objects.count() == 1
    notification = Notification.objects.get(id=1)
    assert not notification.is_read

    response = authorized_client.patch('/api/v1/notification/1/', data=json.dumps(
        {
            "is_read": True
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    notification.refresh_from_db()
    assert notification.is_read


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_notification_fixture")
def test_notification_delete(authorized_client, authorized_user):
    assert Notification.objects.count() == 1

    response = authorized_client.delete('/api/v1/notification/1/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Notification.objects.count() == 0
