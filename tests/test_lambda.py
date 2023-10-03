import os
import sys
from mock import patch
sys.path.append(os.getcwd()+'/gold_api')
from gold_api.api import get_members_by_list_of_id

@patch('gold_api.api.get_all_members')
def test_get_members_by_list_of_id(mock_get_all_members):
    mock_get_all_members.return_value=[]
    assert get_members_by_list_of_id([]) == []
