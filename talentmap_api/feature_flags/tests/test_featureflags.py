import pytest
from model_mommy import mommy
from rest_framework import status

from talentmap_api.feature_flags.models import FeatureFlags


@pytest.fixture
def test_featureflags_fixture():
    if FeatureFlags.objects.first() is None:
        mommy.make(FeatureFlags, feature_flags={"test": 1}, date_updated="01-10-2020 17:34:31:112")


@pytest.mark.usefixtures("test_featureflags_fixture")
@pytest.mark.django_db(transaction=True)
def test_get_featureflags(authorized_client, authorized_user):
    featureflag = FeatureFlags.objects.first()

    response = authorized_client.get('/api/v1/featureflags/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["test"] == featureflag.feature_flags["test"]
