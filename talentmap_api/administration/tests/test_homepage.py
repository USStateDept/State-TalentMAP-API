import pytest
import json

from talentmap_api.administration.models import HomepageBanner

from model_mommy import mommy
from rest_framework import status

@pytest.fixture
def test_homepage_banner_fixture():
  if HomepageBanner.objects.first() is None:
    mommy.make(HomepageBanner, text="Test text", is_visible=True)

@pytest.mark.usefixtures("test_homepage_banner_fixture")
@pytest.mark.django_db(transaction=True)
def test_get_homepage_banner(authorized_client, authorized_user):
  homepage_banner = HomepageBanner.objects.first()

  response = authorized_client.get('/api/v1/homepage/banner/')

  assert response.status_code == status.HTTP_200_OK
  assert response.data["text"] == homepage_banner.text
  assert response.data["is_visible"] == homepage_banner.is_visible

@pytest.mark.usefixtures("test_homepage_banner_fixture")
@pytest.mark.django_db(transaction=True)
def test_patch_homepage_banner(authorized_client, authorized_user):
  group = mommy.make('auth.Group', name='superuser')
  group.user_set.add(authorized_user)

  homepage_banner = HomepageBanner.objects.first()
  
  data = {
    "is_visible": False,
    "text": "Updated test text"
  }

  response = authorized_client.patch('/api/v1/homepage/banner/', 
    data=json.dumps(data), content_type="application/json")

  assert response.status_code == status.HTTP_204_NO_CONTENT

  homepage_banner.refresh_from_db()

  assert homepage_banner.text == data["text"]
  assert homepage_banner.is_visible == data["is_visible"]