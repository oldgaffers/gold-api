import os
import sys
from mock import patch
sys.path.append(os.getcwd()+'/gold_api')
from gold_api.api import get_members_by_list_of_id, get_schema

@patch('gold_api.api.get_all_members')
def test_get_members_by_list_of_id(mock_get_all_members):
    mock_get_all_members.return_value=[]
    assert get_members_by_list_of_id([]) == []

@patch('gold_api.api.put_profile')
@patch('gold_api.bucket_data.get_profile')
@patch('gold_api.api.get_all_members')
def test_mutate(mock_get_all_members, mock_get_profile, mock_put_profile):
    schema = get_schema()
    assert schema.execute(
        'mutation profileMutation { addProfile(id: 559, text: "abc") { ok }}') is not None
    er = schema.execute(
        'mutation profileMutation($id: Int!, $text: String!) { addProfile(id: $id, text: $text) { ok }}',
        variables={
            'id': 559,
            'text': 'a grumpy skipper',
        },
    )
    assert er.data == { 'addProfile': {'ok': False} }