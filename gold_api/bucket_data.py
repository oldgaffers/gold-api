import json 
import boto3

s3 = boto3.client('s3')

keymap = {
  'salutation': 'Salutation', 
  'firstname': 'Firstname', 
  'lastname': 'Lastname', 
  'id': 'ID', 
  'member': 'Member Number', 
  'email': 'Email', 
  'GDPR': 'GDPR', 
  'status': 'Status',
  'town': 'Town',
  'area': 'Area',
  'smallboats': 'Trailer', 
  'interests': 'Interest Areas',
  'mobile': 'Mobile',
  'telephone': 'Telephone',
  'primary': 'Primary',
  'payment': 'Payment Method',
  'type': 'Membership Type',
  'postcode': 'Postcode',
  'address': ['Address1', 'Address2', 'Address3'], 
  'country': 'Country', 
  'yob': 'Year Of Birth', 
  'start': 'Year Joined', 
  'profile': 'profile',
  'crewingprofile': 'crewingprofile',
}

default_values = {
  'salutation': '', 
  'firstname': '', 
  'lastname': '', 
  'id': -1, 
  'member': -1, 
  'email': '', 
  'GDPR': False,
  'smallboats': False, 
  'status': 'Not Paid',
  'town': '',
  'area': '',
  'mobile': '',
  'telephone': '',
  'primary': True,
  'payment': 'unknown',
  'type': 'Single',
  'postcode': '',
  'profile': '',
  'crewingprofile': '',
  'address': [], 
  'country': '', 
  'yob': -1, 
  'start': -1, 
}

def json_from_object(bucket, key):
    r = s3.get_object(Bucket=bucket, Key=key)
    text = r["Body"].read().decode('utf-8')
    return json.loads(text)

def get_augmented(id):
  bucket = 'boatregister'
  key = f"members/{id}.json"
  try:
    return json_from_object(bucket, key)
  except:
    return {}

def put_augmented(member):
  id = member['id']
  existing = get_augmented(id)
  key = f"members/{id}.json"
  try:
    augmented = {**existing, **member}
  except:
    augmented = existing
  s3.put_object(Body=json.dumps(augmented), Bucket='boatregister', Key=key)

def map_member_list_values(keys, member):
  return [member[k] for k in keys]

def map_member(member, augmentations):
  result = {}
  for key in keymap.keys():
    k = keymap[key]
    if type(k) == list:
      result[key] = map_member_list_values(k, member)
    else:
      result[key] = member.get(k, default_values.get(k, None))
  if result['id'] in augmentations:
    return {**result, **augmentations[result['id']]}
  return result

def get_all_augmentations():
  r = {}
  p = s3.list_objects_v2(Bucket='boatregister', Prefix='members/')
  for c in p['Contents']:
    key = c['Key']
    if key.endswith('.json'):
      m = json_from_object('boatregister', key)
      r[m['id']] = m
  return r

def get_all_members():
  members = json_from_object('boatregister', 'gold/latest.json')
  a = get_all_augmentations()
  return [map_member(m, a) for m in members]
