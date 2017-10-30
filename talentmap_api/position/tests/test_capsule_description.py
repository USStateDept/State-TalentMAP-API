import pytest
import json

from django.contrib.auth.models import User

from talentmap_api.position.models import CapsuleDescription

from talentmap_api.common.common_helpers import get_group_by_name

from model_mommy import mommy
from rest_framework import status


@pytest.mark.django_db()
def test_capsule_description_update(authorized_client, authorized_user):
    description = mommy.make(CapsuleDescription, id=1, content="banana", point_of_contact="banana@state.gov", website="google it")
    post = mommy.make("organization.Post", id=1)
    mommy.make("position.Position", post=post, description=description)

    description.position.post.create_permissions()

    response = authorized_client.patch('/api/v1/capsule_description/1/', data=json.dumps(
        {
            "content": "banana splits",
            "point_of_contact": "bananasplit@state.gov",
            "website": "http://www.state.gov"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Give our user appropriate permissions
    group = get_group_by_name("post_editors_1")
    group.user_set.add(authorized_user)

    # Re-get the user from the DB as permissions get cached
    authorized_user = User.objects.get(id=authorized_user.id)
    assert authorized_user.has_perm(f"position.{post.permission_edit_post_capsule_description_codename}")

    response = authorized_client.patch('/api/v1/capsule_description/1/', data=json.dumps(
        {
            "content": "banana splits",
            "point_of_contact": "bananasplit@state.gov",
            "website": "http://www.state.gov"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    description = CapsuleDescription.objects.get(id=1)
    assert description.content == "banana splits"
    assert description.point_of_contact == "bananasplit@state.gov"
    assert description.website == "http://www.state.gov"
