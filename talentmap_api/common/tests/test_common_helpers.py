import pytest
import datetime
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from django.core.exceptions import PermissionDenied

from model_mommy import mommy

from talentmap_api.common.common_helpers import get_permission_by_name, get_group_by_name, in_group_or_403, has_permission_or_403, ensure_date, safe_navigation, load_environment_script
from talentmap_api.position.models import Position


@pytest.mark.django_db()
def test_ensure_date():
    # Try to get a permission without it existing
    with pytest.raises(Exception, match="Parameter must be a date object or string"):
        ensure_date(201225123)

    date = datetime.datetime.strptime("1000-01-01", '%Y-%m-%d').date()

    # Now check it
    assert ensure_date("1000-01-01") == date
    assert ensure_date(date) == date


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
def test_load_environment():
    # Try to load a nonexistent file
    with pytest.raises(Exception):
        load_environment_script('i_dont_exist.sh.existential')

    # Load the test environment script
    env = load_environment_script(os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_setup_environment.sh'))

    assert env['DJANGO_DEBUG']
    assert env['DATABASE_URL'] == 'postgres://username:password@hostname:5432/database_name'
    assert env['DJANGO_SECRET_KEY'] == 'secret_key'
    assert env['DEPLOYMENT_LOCATION'] == '/var/www/talentmap/api/'
