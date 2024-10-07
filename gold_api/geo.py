import boto3
import requests
from bng_latlon import OSGB36toWGS84
from math import radians, sin, cos, asin, sqrt
from ddb_data import add_location, geoval

key = None

def init():
  global key
  if key is None:
    ssm = boto3.client('ssm')
    r = ssm.get_parameter(Name='/OS/API_KEY')
    key = r['Parameter']['Value']

def osfind(place):
  try: 
    r = requests.get('https://api.os.uk/search/names/v1/find', headers={'key': key}, params={'query': place, 'maxresults': 1})
    if r.ok:
      answer = r.json()
      entry = answer['results'][0]['GAZETTEER_ENTRY']
      lat, lng = OSGB36toWGS84(entry['GEOMETRY_X'], entry['GEOMETRY_Y'])
      return { 'name': place, 'lat': lat, 'lng': lng }
  except:
    pass
  return None

def haversine(lon1, lat1, lon2, lat2):
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
  return 2 * 6371 * asin(sqrt(a))

def distance(ll, lng, lat):
  x = ll.get('lng', None)
  y = ll.get('lat', None)
  if x is None or y is None:
      return None
  d = haversine(x, y, lng, lat)
  d = d / 1.852 # km to nm
  d = float(int(10*d)/10)
  return d

def addlatlng(members):
  for member in members:
    if member['country'] in ['Eire', 'United Kingdom'] and len(member['postcode']) > 2 and not 'lat' in member:
      loc = osfind(member['postcode'].replace(' ', ''))
      if loc is not None:
        member['lat'] = geoval(loc['lat'])
        member['lng'] = geoval(loc['lng'])
        add_location(member, loc)

def addproximity(members, lng, lat):
  addlatlng(members)
  m2 = []
  for member in members:
    d = distance(member, lng, lat)
    if d is None:
      m2.append(member)
    else:
      m2.append({**member, 'proximity': d})
  return m2
