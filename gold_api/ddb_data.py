import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal 

keymap = {
  'address': ['address1', 'address2', 'address3'], 
  'member': 'membership',
  'yob': 'year_of_birth', 
  'start': 'year_joined', 
}

dynamodb = None
table = None

def init():
  global dynamodb, table
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
  elif k == 'year of birth':
    return 'yob'
  elif k == 'year joined':
    return 'start'
  return k

def a(row):
  row['address'] = [row['address1'], row['address2'], row['address3']]
  return row

def mapData(data):
  return [{mapKey(k):mapValue(k, v) for (k,v) in a(row).items()} for row in data]

def put_augmented(row):
  global table
  if 'membership' in row:
    membership = row['membership']
  else:
    r = table.scan(FilterExpression=Attr('id').eq(id), ProjectionExpression='membership')
    if r['Count'] != 1:
      return
    membership = r['Items'][0]['membership']
  primary_key = ['id','membership']
  item = {keymap.get(k, k.lower().replace(' ', '_').replace(':', '')):v for (k,v) in row.items()}
  a = [kv for kv in item.items() if kv[0] not in primary_key]
  keys = [kv[0] for kv in a]
  vals = [kv[1] for kv in a]
  id = row['id']
  return table.update_item(
      Key={ 'id': id, 'membership': membership },
      UpdateExpression=f"SET {','.join([f'#f{i}=:var{i}' for i, k in enumerate(keys)])}",
      ExpressionAttributeNames={f'#f{i}':k for i,k in enumerate(keys)},
      ExpressionAttributeValues={f':var{i}':v for i,v in enumerate(vals)},
      ReturnValues="UPDATED_NEW"
  )

def get_all_members():
  global table
  r = table.scan()
  return r['Count'], mapData(r['Items'])

def get_members_by_list_of_memberno(l):
  global table
  if len(l) == 1:
    r = table.query(KeyConditionExpression=Key("membership").eq(l[0]))
  else:
    r = table.scan(FilterExpression=Attr('membership').is_in(l))
  return table.item_count, mapData(r['Items'])

def get_member_by_id(id):
  global table
  r = table.scan(FilterExpression=Attr('id').eq(id))
  if r['Count'] == 1:
    return mapData(r['Items'])[0]
  return None

def get_members_by_list_of_id(l):
  global table
  r = table.scan(FilterExpression=Attr('id').is_in(l))
  return table.item_count, mapData(r['Items'])
