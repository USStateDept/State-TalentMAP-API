import pytest
import datetime
from dateutil import parser, tz

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from django.core.exceptions import PermissionDenied, ValidationError

from model_mommy import mommy

from talentmap_api.common.common_helpers import get_permission_by_name, get_group_by_name, in_group_or_403, has_permission_or_403, ensure_date, safe_navigation, order_dict, serialize_instance, in_superuser_group, validate_filters_exist
from talentmap_api.position.models import Position
from talentmap_api.bidding.filters import CyclePositionFilter


@pytest.mark.django_db()
def test_ensure_date():
    # Try to get a permission without it existing
    with pytest.raises(Exception, match="Parameter must be a date object or string"):
        ensure_date(201225123)

    date = parser.parse("1000-01-01T00:00:00-05:00")

    # Now check it
    assert ensure_date("1000-01-01", utc_offset=-5) == date


@pytest.mark.django_db()
def test_serialize_instance():
    # Try to get a permission without it existing
    p = mommy.make('position.Position')
    assert serialize_instance(p, 'talentmap_api.position.serializers.PositionSerializer').get('id') == p.id


@pytest.mark.django_db()
def test_order_dict():
    ordered_dict = {
        "a": 1,
        "b": 2,
        "c": 3
    }

    unordered_dict = {
        "b": 2,
        "a": 1,
        "c": 3
    }

    assert order_dict(unordered_dict) == ordered_dict

    nested_ordered_dict = {
        "a": 1,
        "b": {
            "a": 1,
            "b": 2,
            "c": 3
        },
        "c": 3
    }

    nested_unordered_dict = {
        "b": {
            "b": 2,
            "a": 1,
            "c": 3
        },
        "a": 1,
        "c": 3
    }

    assert order_dict(nested_unordered_dict) == nested_ordered_dict


@pytest.mark.django_db()
def test_safe_navigation():
    position = mommy.make('position.Position')

    assert safe_navigation(position, "post") is None

    position.post = mommy.make('organization.Post')
    position.save()

    assert safe_navigation(position, "post") is not None
    assert safe_navigation(position, "post.location") is None

    position.post.location = mommy.make('organization.Location')
    position.save()

    assert safe_navigation(position, "post.location") is not None


@pytest.mark.django_db()
def test_get_permission_by_name():
    # Try to get a permission without it existing
    with pytest.raises(Exception, match="Permission position.test_permission not found."):
        get_permission_by_name("position.test_permission")

    # Create a permission
    mommy.make('auth.Permission', name="test_permission", codename="test_permission", content_type=ContentType.objects.get_for_model(Position))

    # Now check it
    assert get_permission_by_name("position.test_permission")


@pytest.mark.django_db()
def test_has_permission_or_403(authorized_user):
    # Create a permission
    permission = mommy.make('auth.Permission', name="test_permission", codename="test_permission", content_type=ContentType.objects.get_for_model(Position))

    # Check for 403 since we don't have permission
    with pytest.raises(PermissionDenied):
        has_permission_or_403(authorized_user, "position.test_permission")

    # Add the permission to the user
    authorized_user.user_permissions.add(permission)

    # Should not raise an exception (we re-get the user due to permission caching)
    has_permission_or_403(User.objects.get(id=authorized_user.id), "position.test_permission")


@pytest.mark.django_db()
def test_get_group_by_name():
    # Try to get a permission without it existing
    with pytest.raises(Exception, message="Group test_group not found."):
        get_group_by_name("test_group")

    # Create a permission
    mommy.make('auth.Group', name="test_group")

    # Now check it
    assert get_group_by_name("test_group")


@pytest.mark.django_db()
def test_in_group_or_403(authorized_user):
    group = mommy.make('auth.Group', name="test_group")

    # Check for 403 since we're not in the group
    with pytest.raises(PermissionDenied):
        in_group_or_403(authorized_user, "test_group")

    # Add the user to the group
    group.user_set.add(authorized_user)

    # Should not raise an exception
    in_group_or_403(authorized_user, "test_group")


@pytest.mark.django_db()
def test_in_superuser_group(authorized_user):
    group = mommy.make('auth.Group', name="superuser")

    assert not in_superuser_group(authorized_user)

    # Add the user to the group
    group.user_set.add(authorized_user)

    # Should not raise an exception
    assert in_superuser_group(authorized_user)

@pytest.mark.django_db()
def test_validate_filters_exist(authorized_user):
    validate_filters_exist({"position__skill__code__in": '1'}, CyclePositionFilter)
    validate_filters_exist({"is_domestic": True}, CyclePositionFilter)

    # Check for 403 since we're not in the group
    with pytest.raises(ValidationError, match="Filter position__is_domestic is not valid on this endpoint"):
        validate_filters_exist({"position__is_domestic": True}, CyclePositionFilter)
