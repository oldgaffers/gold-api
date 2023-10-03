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
  'postcode': 'Postcode'
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
}

def json_from_object(bucket, key):
    r = s3.get_object(Bucket=bucket, Key=key)
    text = r["Body"].read().decode('utf-8')
    return json.loads(text)

def get_profile(member):
  try:
    augmented = json_from_object('boatregister', f"members/{member['id']}.json")
    return augmented['profile']
  except:
    return ''

def put_profile(member):
  key = f"members/{member['id']}.json"
  try:
    augmented = json_from_object('boatregister', key)
  except:
    augmented = {}
  augmented['profile'] = member['profile']
  s3.put_object(Body=json.dumps(augmented), Bucket='boatregister', Key=key)

def map_member(member):
  result = {}
  for key in keymap.keys():
    k = keymap[key]
    if k in member:
      result[key] = member[k]
    else:
      result[key] = default_values[key]
  return result

def get_all_members():
  members = json_from_object('boatregister', 'gold/latest.json')
  return [map_member(m) for m in members]
