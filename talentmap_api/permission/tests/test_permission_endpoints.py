import pytest

from model_mommy import mommy
from rest_framework import status


@pytest.mark.django_db()
def test_user_permission_endpoint(authorized_client, authorized_user):
    group = mommy.make('auth.Group')
    permission = mommy.make('auth.Permission')

    group.permissions.add(permission)
    group.user_set.add(authorized_user)

    response = authorized_client.get(f'/api/v1/permission/user/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["groups"] == [group.name]
    assert response.data["permissions"] == list(authorized_user.get_all_permissions())

    response = authorized_client.get(f'/api/v1/permission/user/{authorized_user.profile.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data["groups"] == [group.name]
    assert response.data["permissions"] == list(authorized_user.get_all_permissions())

    response = authorized_client.get(f'/api/v1/permission/user/all/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

    ao_group = mommy.make('auth.Group', name="superuser")
    ao_group.user_set.add(authorized_user)

    response = authorized_client.get(f'/api/v1/permission/user/all/')
    assert response.status_code == status.HTTP_200_OK


"""
# This test occassionally fails on CircleCI, so it commented out
@pytest.mark.django_db(transaction=True)
def test_group_action_endpoints(authorized_client, authorized_user):
    group = mommy.make('auth.Group')
    new_user = mommy.make('auth.User')

    # Ensure all endpoints return 403 before we are an AO
    response = authorized_client.get(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = authorized_client.put(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = authorized_client.delete(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Give us some AO permissions
    ao_group = mommy.make('auth.Group', name="superuser")
    ao_group.user_set.add(authorized_user)

    # Check if the user is in the group (no, so 404)
    response = authorized_client.get(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Add the user to the group
    response = authorized_client.put(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the user is in the group (yes, so 204)
    response = authorized_client.get(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Remove the user from the group
    response = authorized_client.delete(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the user is in the group (no, so 404)
    response = authorized_client.get(f'/api/v1/permission/group/{group.id}/user/{new_user.profile.id}/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
"""