import json
import pytest
from model_mommy import mommy
from rest_framework import status

from talentmap_api.administration.models import AboutPage


@pytest.fixture
def test_aboutpage_fixture():
    if AboutPage.objects.first() is None:
        mommy.make(AboutPage, content="*Test about page*")


@pytest.mark.usefixtures("test_aboutpage_fixture")
@pytest.mark.django_db(transaction=True)
def test_get_aboutpage(authorized_client, authorized_user):
    about_page = AboutPage.objects.first()

    response = authorized_client.get('/api/v1/aboutpage/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["content"] == about_page.content


@pytest.mark.usefixtures("test_aboutpage_fixture")
@pytest.mark.django_db(transaction=True)
def test_patch_homepage_banner(authorized_client, authorized_user):
    group = mommy.make('auth.Group', name='superuser')
    group.user_set.add(authorized_user)

    about_page = AboutPage.objects.first()

    data = {
        "content": "** Updated test homepage **"
    }

    response = authorized_client.patch('/api/v1/aboutpage/',
                                       data=json.dumps(data), content_type="application/json")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    about_page.refresh_from_db()

    assert about_page.content == data["content"]
