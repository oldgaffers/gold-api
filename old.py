import json 
import boto3
from datetime import date
from graphene.types.scalars import Boolean
from graphene import Field, Int, List, ObjectType, String, Schema, Mutation

s3 = boto3.client('s3')

def json_from_object(bucket, key):
    r = s3.get_object(Bucket=bucket, Key=key)
    text = r["Body"].read().decode('utf-8')
    return json.loads(text)
    
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

def get_members_by_id_and_memberno(no, id):
  members = get_all_members()
  return list(filter(lambda member: member['id'] == id and member['member'] == no, members))

def get_members_by_list_of_memberno(l):
  members = get_all_members()
  return list(filter(lambda member: member['member'] in l, members))

def get_members_by_list_of_id(l):
  members = get_all_members()
  return list(filter(lambda member: member['id'] in l, members))
  
def get_members_by_field(value, field):
  members = get_all_members()
  return list(filter(lambda member: member[field] == value, members))

def get_members_by_memberno(no):
  return get_members_by_field(no, 'member')

def get_members_by_id(id):
  return get_members_by_field(id, 'id')

class Member(ObjectType):
    id = Int()
    member = Int()
    salutation = String()
    firstname = String()
    lastname = String()
    status = String()
    email = String()
    GDPR = Boolean()
    smallboats = Boolean()
    town = String()
    area = String()
    telephone = String()
    mobile = String()
    postcode = String()
    interests = List(String)
    primary = Boolean()
    type = String()
    payment = String()
    profile = String()

class Query(ObjectType):
    members = List(Member,
      id=Int(),
      member=Int(),
      firstname=String(),
      lastname=String(),
      members=List(Int),
      ids=List(Int),
    )

    def resolve_members(root, info, **args):
      k = list(args.keys())
      # print('K', args)
      if 'members' in k:
        members = get_members_by_list_of_memberno(args['members'])
        k.remove('members')
      elif 'ids' in k:
        members = get_members_by_list_of_id(args['ids'])
        # print('k', args, members) 
        k.remove('ids')
      else:
        members = get_all_members()
      for field in k:
        members = list(filter(lambda member: member[field] == args[field], members))
      for m in members:
        m['profile'] = get_profile(m)
      answers = members
      # print(f"return {answers}")
      return answers

class AddProfile(Mutation):
    class Arguments:
        id = String()
        text = String()

    ok = Boolean()

    def mutate(root, info, id, text):
      print('mutate', root, info, id, text)
      ok = True
      put_profile({ 'id': id, 'profile': text })
      return AddProfile(ok=ok)
        
class MyMutations(ObjectType):
    addProfile = AddProfile.Field()

schema = Schema(query=Query, mutation=MyMutations)

def lambda_handler(event, context):
  # print(json.dumps(event))
  if 'body' in event and event['body'] is not None:
    body = json.loads(event['body'])
    if 'variables' in body:
      print(body['query'], body['variables'])
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


