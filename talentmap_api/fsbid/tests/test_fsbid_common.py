import pytest
from talentmap_api.fsbid.services.common import get_bid_stats_for_csv


def test_get_bid_stats_for_csv():
    mock = {
        'bid_statistics': [{'total_bids': 10, 'in_grade': 3, 'at_skill': 3, 'in_grade_at_skill': 2}]
    }
    res = get_bid_stats_for_csv(mock)
    assert res == '10(3/3)2'

    mock = {
        'bid_statistics': [{'total_bids': 0, 'in_grade': 0, 'at_skill': 0, 'in_grade_at_skill': 0}]
    }
    res = get_bid_stats_for_csv(mock)
    assert res == '0(0/0)0'

    mock = {
        'bid_statistics': [{'total_bids': 0, 'in_grade': None, 'at_skill': 0, 'in_grade_at_skill': 0}]
    }
    res = get_bid_stats_for_csv(mock)
    assert res == 'N/A'

    mock = {}
    res = get_bid_stats_for_csv(mock)
    assert res == 'N/A'