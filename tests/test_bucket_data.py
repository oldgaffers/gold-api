import os
import sys
from mock import patch
sys.path.append(os.getcwd()+'/gold_api')
from gold_api.bucket_data import get_members_by_list_of_id

test_member = {
        'id': 559,
        'salutation': '',
        'firstname': '',
        'lastname': '',
        'member': 0,
        'GDPR': False,
        'smallboats': False,
        'youngermember': False,
        'status': '',
        'telephone': '',
        'mobile': '',
        'area': '',
        'town': '',
        'interests': [],
        'email': '',
        'primary': True,
        'skipper': { 'text': 'careful' },
        'crewing': { 'text': 'some text' },
        'postcode': '',
        'type': '',
        'payment': '',
        'address': [''],
        'country': '',
        'yob': 0,
        'start': 0,
    }

@patch('gold_api.bucket_data.get_all_members')
def test_get_members_by_list_of_id(mock_get_all_members):
    mock_get_all_members.side_effect=[],[{'id': 559}]
    total, members = get_members_by_list_of_id([])
    assert members == []
    assert total == 0
    total, members = get_members_by_list_of_id([559])
    assert members == [{'id': 559}]
