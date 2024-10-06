import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal 

# fields to exclude from results by default
exclude = ['lat', 'lng']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('members')

def mapValue(k, v):
  print(k, v)
  if k == 'lat' or k == 'lng':
    return float(v)
  if isinstance(v, Decimal):
    return int(v)
  return v

def mapData(data, exclude):
  return [{k:mapValue(k, v) for (k,v) in row.items() if not k in exclude} for row in data]
  
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

def get_members_by_id(id):
  global table, exclude
  r = table.query(KeyConditionExpression=Key("id").eq(id))
  return table.item_count, mapData(r['Items'], exclude)

def get_members_by_list_of_id(l):
  global table, exclude
  r = table.scan(FilterExpression=Attr('id').is_in(l))
  return table.item_count, mapData(r['Items'], exclude)
