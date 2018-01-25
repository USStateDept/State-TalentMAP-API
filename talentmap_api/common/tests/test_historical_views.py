import pytest

from rest_framework import status
from freezegun import freeze_time
from model_mommy import mommy


@pytest.mark.django_db()
def test_post_historical_view(client):
    with freeze_time("1990-01-01T00:00:00Z") as frozen_time:
        tod = mommy.make('organization.TourOfDuty', long_description="2YR", months=24)
        post = mommy.make('organization.Post', danger_pay=10, differential_rate=10, tour_of_duty=tod)

        frozen_time.move_to("1995-01-01T00:00:00Z")
        post.danger_pay = 0
        post.differential_rate = 0
        post.save()

        tod.months = 12
        tod.long_description = "1YR"
        tod.save()

        response = client.get(f'/api/v1/orgpost/{post.id}/history/')

        assert len(response.data["results"]) == 2

        response = client.get(f'/api/v1/orgpost/{post.id}/history/?history_date__lte=1993-01-01T00:00:00Z')

        assert len(response.data["results"]) == 1
