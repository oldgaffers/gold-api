import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal 
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

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
  try:
    if k == 'lat' or k == 'lng':
      if v == Decimal(0):
        return None
      fv = float(v)
      return fv
    if isinstance(v, Decimal):
      return int(v)
  except:
    print('error in mapValue', k, v)
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
  try:
    row['address'] = [row['address1'], row['address2'], row['address3']]
  except:
    print('error in address', row)
  return row

def mapData(data):
  return [{mapKey(k):mapValue(k, v) for (k,v) in a(row).items()} for row in data]

def partial_update(row):
    global table
    primary_key = ['id','membership']
    item = {keymap.get(k, k.lower().replace(' ', '_').replace(':', '')):v for (k,v) in row.items()}
    a = [kv for kv in item.items() if kv[0] not in primary_key]
    keys = [kv[0] for kv in a]
    vals = [kv[1] for kv in a]
    return table.update_item(
        Key={ 'id':item['id'], 'membership':item['membership'] },
        UpdateExpression=f"SET {','.join([f'#f{i}=:var{i}' for i, k in enumerate(keys)])}",
        ExpressionAttributeNames={f'#f{i}':k for i,k in enumerate(keys)},
        ExpressionAttributeValues={f':var{i}':v for i,v in enumerate(vals)},
        ReturnValues="UPDATED_NEW"
    )

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

def get_total():
  return table.item_count

def get_all_members():
  global table
  r = table.scan()
  print('G', r['Count'])
  return r['Count'], mapData(r['Items'])

def get_members_by_list_of_memberno(l):
  global table
  if len(l) == 1:
    r = table.query(KeyConditionExpression=Key("membership").eq(l[0]))
    return table.item_count, mapData(r['Items'])
  else:
    r = table.scan(FilterExpression=Attr('membership').is_in(l))
    return r['Count'], mapData(r['Items'])

def get_member_by_id(id):
  global table
  r = table.scan(FilterExpression=Attr('id').eq(id))
  if r['Count'] == 1:
    return mapData(r['Items'])[0]
  return None

def get_members_by_list_of_id(l):
  global table
  r = table.scan(FilterExpression=Attr('id').is_in(l))
  return r['Count'], mapData(r['Items'])

def geoval(f):
  return round(Decimal(f), 5)

def add_location(item, loc):
  lat = geoval(loc['lat'])
  lng = geoval(loc['lng'])
  membership = item.get('membership', item.get('member', None))
  partial_update({ 'id': item['id'], 'membership': membership, 'lat': lat, 'lng': lng })
