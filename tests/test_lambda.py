import os
import sys
from mock import patch
sys.path.append(os.getcwd()+'/gold_api')
from gold_api.lambda_function import lambda_handler

@patch('gold_api.api.get_schema')
def test_get_members_by_list_of_id(mock_get_schema):
    assert lambda_handler({}, None) == { 'statusCode': 200, 'body': '{"data": "GET does nothing"}' }
