import os
import sys
from mock import patch
sys.path.append(os.getcwd()+'/gold_api')
from gold_api.api import get_members_by_list_of_id, get_schema

test_member = {
        'id': 559,
        'salutation': '',
        'firstname': '',
        'lastname': '',
        'member': 0,
        'GDPR': False,
        'smallboats': False,
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

@patch('gold_api.api.get_members_by_list_of_memberno')
@patch('gold_api.api.get_members_by_list_of_id')
@patch('gold_api.api.get_all_members')
@patch('gold_api.api.add_proximity')
@patch('gold_api.api.get_total')
def test_get_count(mock_get_total, mock_add_proximity, mock_get_all_members, mock_get_members_by_list_of_id, mock_get_members_by_list_of_memberno):
    mock_get_members_by_list_of_memberno.return_value=1,[{'id': 559}]
    mock_get_all_members.return_value=1,[{'id': 559}]
    mock_get_members_by_list_of_id.return_value=1,[{'id': 559}]
    mock_add_proximity.return_value=[{'id': 559}]
    mock_get_total.return_value=1
    schema = get_schema()
    er = schema.execute(
        'query m($id: Int!) { total members(id: $id) { id } }',
        variables={
            'id': 559,
        },
    )
    assert er.data == {'members': [{'id': 559}], 'total': 1}

@patch('gold_api.api.get_members_by_list_of_id')
def test_query_by_list_of_id(mock_get_members_by_list_of_id):
    mock_get_members_by_list_of_id.return_value=1, [test_member]
    schema = get_schema()
    er = schema.execute(
        'query members($ids: [Int]!) { members(ids: $ids) { id }}',
        variables={
            'ids': [559],
        },
    )
    assert er.data == { 'members': [{ 'id': 559 }]}    
    er = schema.execute(
        'query members($ids: [Int]!) { members(ids: $ids) { id skipper{ text } crewing{ text } salutation firstname lastname member id GDPR smallboats status telephone mobile area town interests email primary postcode type payment address country yob start __typename }}',
        variables={
            'ids': [559],
        },
    )
    assert er.data == { 'members': [{**test_member, '__typename': 'Member'}]}

@patch('gold_api.api.put_augmented')
@patch('gold_api.api.get_member_by_id')
def test_add_skipper_profile_bad(mock_get_member_by_id, mock_put_augmented):
    mock_get_member_by_id.return_value = None
    mock_put_augmented.return_value = None
    schema = get_schema()
    er = schema.execute(
        'mutation m($id: Int!, $profile: ProfileInput!) { addSkipperProfile(id: $id, profile: $profile) { ok }}',
        variables={
            'id': 559,
            'profile': {
                'text': 'a grumpy skipper',
            }
        },
    )
    assert er.data == { 'addSkipperProfile': {'ok': False} }

@patch('gold_api.api.put_augmented')
@patch('gold_api.api.get_member_by_id')
def test_add_skipper_profile_good(mock_get_member_by_id, mock_put_augmented):
    mock_get_member_by_id.return_value = { 'id': 559 }
    mock_put_augmented.return_value = None
    schema = get_schema()
    er = schema.execute(
        'mutation m($id: Int!, $profile: ProfileInput!) { addSkipperProfile(id: $id, profile: $profile) { ok, member { id } }}',
        variables={
            'id': 559,
            'profile': {
                'text': 'a grumpy skipper',
            }
        },
    )
    assert er.data is not None
    r = er.data['addSkipperProfile']
    assert r['ok']
    assert r['member'] == { 'id': 559}

@patch('gold_api.api.put_augmented')
@patch('gold_api.api.get_member_by_id')
def test_add_crewing_profile_good(mock_get_member_by_id, mock_put_augmented):
    mock_get_member_by_id.return_value = { 'id': 559 }
    mock_put_augmented.return_value = None
    schema = get_schema()
    er = schema.execute(
        'mutation m($id: Int!, $profile: ProfileInput!) { addCrewingProfile(id: $id, profile: $profile) { ok, member { id } }}',
        variables={
            'id': 559,
            'profile': {
                'text': 'a grumpy crew member',
            }
        },
    )
    assert er.data is not None
    r = er.data['addCrewingProfile']
    assert r['ok']
    assert r['member'] == { 'id': 559}