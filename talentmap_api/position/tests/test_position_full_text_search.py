import pytest

from model_mommy import mommy
from rest_framework import status


# Might move this fixture to a session fixture if we end up needing languages elsewhere
@pytest.fixture
def test_position_fts_fixture():
    # Create some junk positions to add numbers
    bc = mommy.make('bidding.BidCycle', active=True)
    
    pos1 = (mommy.make('position.Position',
                                organization__long_description="German Embassy",
                                bureau__long_description="German Embassy",
                                skill__description="Doctor",
                                languages__language__long_description="German"))                          
    pos2 = (mommy.make('position.Position',
                                organization__long_description="French Embassy",
                                bureau__long_description="French Embassy",
                                skill__description="Doctor",
                                languages__language__long_description="French"))

    pos3 = (mommy.make('position.Position',
                                organization__long_description="French Attache",
                                bureau__long_description="French Attache",
                                skill__description="Colorguard",
                                languages__language__long_description="French"))
    bc.positions.add(pos1)
    bc.positions.add(pos2)
    bc.positions.add(pos3)
    


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_fts_fixture")
@pytest.mark.parametrize("term, expected_count", [
    ("embassy", 2),
    ("embassy doctor", 2),
    ("doctor", 2),
    ("german doctor", 1),
    ("french doctor", 1),
])
def test_available_filtering(client, term, expected_count):
    response = client.get(f'/api/v1/position/?q={term}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == expected_count
