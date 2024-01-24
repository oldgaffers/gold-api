import json
import urllib.request
from api import get_schema
from geo import init

schema = get_schema()

init()

def get_user(event):
  auth = event['headers']['authorization']
  authorizer = event['requestContext']['authorizer']
  aud = authorizer['claims']['aud']
  aud = aud.replace('[','').replace(']','').split(' ')
  ui = next((url for url in aud if 'userinfo' in url), None)
  req = urllib.request.Request(ui, headers={'authorization': auth})
  with urllib.request.urlopen(req) as response:
    user = json.loads(response.read())
  return user

def lambda_handler(event, context):
  # print(json.dumps(event))
  if 'headers' in event:
    user = get_user(event)
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

