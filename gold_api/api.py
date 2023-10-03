from graphene.types.scalars import Boolean
from graphene import Field, Int, List, ObjectType, String, Schema, Mutation
from bucket_data import get_all_members, get_profile, put_profile

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
        id = Int()
        text = String()

    ok = Boolean()
    member = Field(lambda: Member)

    def mutate(self, info, id, text):
      print('mutate', info, id, text)
      members = get_members_by_id(id)
      if len(members) != 1:
        return AddProfile(ok=False)
      ok = True
      member = members[0]
      member['profile'] = text
      put_profile({ 'id': id, 'profile': text })
      return AddProfile(ok=ok, member=member)

class MyMutations(ObjectType):
  addProfile = AddProfile.Field()

def get_schema():
  return Schema(query=Query, mutation=MyMutations)

