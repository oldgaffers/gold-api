from graphene.types.scalars import Boolean
from graphene import (
  Field, Float, Int, InputObjectType, List, 
  Mutation, ObjectType, String, Schema
)
from ddb_data import put_augmented
from ddb_data import get_all_members, get_members_by_list_of_memberno, get_members_by_list_of_id, get_member_by_id
from geo import addproximity

class ProfileInput(InputObjectType):
  text = String()
  pictures = List(String)
  published = Boolean()

class Profile(ObjectType):
  text = String()
  pictures = List(String)
  published = Boolean()
  
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
  address = List(String)
  country = String()
  yob = Int()
  start = Int()
  skipper = Field(Profile)
  crewing = Field(Profile)
  proximity = Float()

extrakeys = ['members', 'ids', 'lat', 'lng', 'after', 'size', 'start', 'sortby', 'sortdir']

class Query(ObjectType):
    
    all_members = None

    total = Int()
    members = List(Member,
      id=Int(),
      member=Int(),
      firstname=String(),
      lastname=String(),
      members=List(Int),
      ids=List(Int),
      lat=Float(),
      lng=Float(),
      after=String(),
      start=Int(),
      size=Int(),
      sortby=String(),
      sortdir=String(),
    )

    def resolve_total(root, info, **args):
      return len(get_all_members())

    def resolve_members(root, info, **args):
      k = list(args.keys())
      start = args.get('start', 0)
      size = args.get('size', 100000)
      after = args.get('after', '0')
      lat = args.get('lat', None)
      lng = args.get('lng', None)
      sortby = args.get('sortby', 'id')
      reverse = args.get('sortdir', 'asc') == 'desc'
      if 'members' in k:
        total, members = get_members_by_list_of_memberno(args['members'])
      elif 'ids' in k:
        total, members = get_members_by_list_of_id(args['ids'])
      else:
        total, members = get_all_members()
      k = [key for key in k if key not in extrakeys]
      for field in k:
        members = list(filter(lambda member: member[field] == args[field], members))
      members.sort(key=lambda x : x[sortby], reverse=reverse)
      members = [m for m in members if f'{m[sortby]}' > after][start:start+size]
      if lat is not None and lng is not None:
        members = addproximity(members, lng, lat)
      answers = members
      return answers

class AddSkipperProfile(Mutation):
    class Arguments:
        id = Int(required=True)
        profile = ProfileInput(required=True)

    ok = Boolean()
    member = Field(lambda: Member)

    def mutate(self, info, id, profile):
      # print('skipper mutate', id, profile)
      member = get_member_by_id(id)
      if member is None:
        return AddSkipperProfile(ok=False)
      ok = True
      member['skipper'] = profile
      put_augmented({ 'id': id, 'skipper': profile })
      return AddSkipperProfile(ok=ok, member=member)

class AddCrewingProfile(Mutation):
    class Arguments:
        id = Int(required=True)
        profile = ProfileInput(required=True)

    ok = Boolean()
    member = Field(lambda: Member)

    def mutate(self, info, id, profile):
      member = get_member_by_id(id)
      if member is None:
        return AddCrewingProfile(ok=False)
      ok = True
      member['crewing'] = profile
      put_augmented({ 'id': id, 'crewing': profile })
      return AddCrewingProfile(ok=ok, member=member)

class MyMutations(ObjectType):
  addSkipperProfile = AddSkipperProfile.Field()
  addCrewingProfile = AddCrewingProfile.Field()

def get_schema():
  return Schema(query=Query, mutation=MyMutations)
