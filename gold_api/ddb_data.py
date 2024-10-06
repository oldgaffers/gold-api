import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal 

# fields to exclude from results by default
exclude = ['lat', 'lng']

keymap = {
  'address': ['address1', 'address2', 'address3'], 
  'member': 'membership',
  'yob': 'year_of_birth', 
  'start': 'year_joined', 
}

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('members')

def mapValue(k, v):
  if k == 'lat' or k == 'lng':
    return float(v)
  if isinstance(v, Decimal):
    return int(v)
  return v

def mapKey(k):
  if k == 'membership':
    return 'member'
  elif k == 'year_of_birth':
    return 'yob'
  elif k == 'year_joined':
    return 'start'
  return k

def mapData(data, exclude):
  return [{mapKey(k):mapValue(k, v) for (k,v) in row.items() if not k in exclude} for row in data]

def put_augmented():
  pass

def get_all_members():
  global table, exclude
  r = table.scan()
  return r['Count'], mapData(r['Items'], exclude)

def get_members_by_list_of_memberno(l):
  global table, exclude
  if len(l) == 1:
    r = table.query(KeyConditionExpression=Key("membership").eq(l[0]))
  else:
    r = table.scan(FilterExpression=Attr('membership').is_in(l))
  return table.item_count, mapData(r['Items'], exclude)

def get_member_by_id(id):
  global table, exclude
  r = table.query(KeyConditionExpression=Key("id").eq(id))
  if r['Count'] == 1:
    return mapData(r['Items'], exclude)[0]
  return None

def get_members_by_list_of_id(l):
  global table, exclude
  r = table.scan(FilterExpression=Attr('id').is_in(l))
  return table.item_count, mapData(r['Items'], exclude)
