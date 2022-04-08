import pytest
import datetime

def test_get_bid_stats_for_csv():
    from talentmap_api.fsbid.services.common import get_bid_stats_for_csv

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


def test_sort_bids():
    from talentmap_api.fsbid.services.common import sort_bids

    mock_bids = [
        {'id': 1, 'status': 'declined', 'create_date': datetime.datetime(2022, 5, 17),
         'position_info': {'position': {'post': {'location': {'city': 'Alpharetta'}}}}},
        {'id': 2, 'status': 'closed', 'create_date': datetime.datetime(2022, 5, 12),
         'position_info': {'position': {'post': {'location': {'city': 'Denver'}}}}},
        {'id': 3, 'status': 'handshake_offered', 'create_date': datetime.datetime(2022, 5, 20),
         'position_info': {'position': {'post': {'location': {'city': 'Washington'}}}}},
        {'id': 4, 'status': 'in_panel', 'create_date': datetime.datetime(2022, 5, 11),
         'position_info': {'position': {'post': {'location': {'city': 'Bethesda'}}}}},
        {'id': 5, 'status': 'submitted', 'create_date': datetime.datetime(2022, 5, 14),
         'position_info': {'position': {'post': {'location': {'city': None}}}},
         }]

    bids = sort_bids(mock_bids, 'status')
    assert bids[0]['id'] == 4
    assert bids[1]['id'] == 3
    assert bids[2]['id'] == 5
    assert bids[3]['id'] == 2
    assert bids[4]['id'] == 1

    bids = sort_bids(mock_bids, '-status')
    assert bids[0]['id'] == 1
    assert bids[1]['id'] == 2
    assert bids[2]['id'] == 5
    assert bids[3]['id'] == 3
    assert bids[4]['id'] == 4

    bids = sort_bids(mock_bids, 'bidlist_create_date')
    assert bids[0]['id'] == 4
    assert bids[1]['id'] == 2
    assert bids[2]['id'] == 5
    assert bids[3]['id'] == 1
    assert bids[4]['id'] == 3

    bids = sort_bids(mock_bids, 'bidlist_location')
    assert bids[0]['id'] == 5  # empty strings come first
    assert bids[1]['id'] == 1
    assert bids[2]['id'] == 4
    assert bids[3]['id'] == 2
    assert bids[4]['id'] == 3


def test_convert_to_fsbid_ql():
    from talentmap_api.fsbid.services.common import convert_to_fsbid_ql

    filters = []
    res = convert_to_fsbid_ql(filters)
    assert res == []

    filters = [{'col': 'aiperdetseqnum', 'val': 6}]
    res = convert_to_fsbid_ql(filters)
    assert res == ['aiperdetseqnum|EQ|6|']

    filters = [{'col': 'aiperdetseqnum', 'val': 6, 'com': 'IN'}]
    res = convert_to_fsbid_ql(filters)
    assert res == ['aiperdetseqnum|IN|6|']

    filters = [
        {'col': 'col1', 'val': 6},
        {'val': 6, 'com': 'IN'},
        {'col': 'col3', 'val': 4, 'com': 'IN'},
        {'col': 'col4', 'com': 'IN'}
    ]
    res = convert_to_fsbid_ql(filters)
    assert res == [
        'col1|EQ|6|',
        'col3|IN|4|'
    ]

def test_map_return_template_cols():
    from talentmap_api.fsbid.services.common import map_return_template_cols

    cols = ['name', 'id', 'cp_id', 'pmi_seq_num']

    cols_mapping = {
        'name': 'wsname',
        'id': 'wsid',
        'cp_id': 'wscpid',
        'pmi_seq_num': 'wspmiseqnum',
        'address': 'wsaddress',
        'phone': 'wsphone',
        'ted': 'wsted',
        'pos': 'wspos',
    }

    data1 = {
        "wsname": 'Tarek',
        "wsaddress": '123 abc drive',
        "wscpid": '7558',
        "wsphone": None,
        "wsted": "2025-06-15T00:00:00.000Z",
        "wspmiseqnum": None,
    }

    res = map_return_template_cols(cols, cols_mapping, data1)

    assert res == {
        "name": 'Tarek',
        "id": None,
        "cp_id": '7558',
        "pmi_seq_num": None,
    }

    data2 = {
        "wsname": 'Jenny',
        "wsid": 4,
        "wsaddress": '456 def drive',
        "wscpid": '65438',
        "wsphone": '202-111-1111',
        "wsted": '2023-06-15T00:00:00.000Z',
        "wspmiseqnum": '999999',
    }

    res = map_return_template_cols(cols, cols_mapping, data2)

    assert res == {
        "name": 'Jenny',
        "id": 4,
        "cp_id": "65438",
        "pmi_seq_num": '999999',
    }
