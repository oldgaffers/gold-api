import json 
from api import get_schema

schema = get_schema()

def lambda_handler(event, context):
  # print(json.dumps(event))
  if 'body' in event and event['body'] is not None:
    body = json.loads(event['body'])
    if 'variables' in body:
      result = schema.execute(body['query'], variables=body['variables'])
    else:
      result = schema.execute(body['query'])
    return {
        'statusCode': 200,
        'headers': {
          'access-control-allow-origin': 'https://oga.org.uk,https://www.oga.org.uk,http:localhost:3000'
        },
        'body': json.dumps({ 'data': result.data })
    }
  return {
      'statusCode': 200,
      'body': json.dumps({ 'data': 'GET does nothing' })
  }

