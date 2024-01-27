import boto3
import requests
from bng_latlon import OSGB36toWGS84
from math import radians, sin, cos, asin, sqrt
from datetime import datetime

key = None
dynamodb = None

def init():
    global key
    global dynamodb
    if key is None:
        ssm = boto3.client('ssm')
        r = ssm.get_parameter(Name='/OS/API_KEY')
        key = r['Parameter']['Value']
        dynamodb = boto3.resource('dynamodb')

def findnet(place):
    try: 
        r = requests.get('https://api.os.uk/search/names/v1/find', headers={'key': key}, params={'query': place, 'maxresults': 1})
        if r.ok:
            answer = r.json()
            entry = answer['results'][0]['GAZETTEER_ENTRY']
            lat, lng = OSGB36toWGS84(entry['GEOMETRY_X'], entry['GEOMETRY_Y'])
            return { 'name': place, 'lat': f'{lat}', 'lng': f'{lng}' }
    except:
        pass
    return None

def find(p):
    if p is None:
        return None
    place = f'{p}'.strip()
    if place == '':
        return None
    ddb_table = dynamodb.Table('geonames_cache')
    r = ddb_table.get_item(Key={ 'name': place })
    if 'Item' in r:
      item = r['Item']
      data = { 'place': place, 'latitude': float(item['lat']), 'longitude': float(item['lng']) }
      return data
    data = findnet(place)
    if data is not None:
        item = {**data, 'timestamp':  int(datetime.utcnow().timestamp()) + 86400 }
        ddb_table.put_item(Item=item)
        result = { 'place': place, 'latitude': data['lat'], 'longitude': data['lng'] }
        return result
    else:
        print('error', r)

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))

def distance(ll, lng, lat): 
    d = haversine(float(ll['lng']), float(ll['lat']), lng, lat)
    d = d / 1.852
    d = float(int(10*d)/10)
    return d

def addproximity(members, lng, lat):
    ddb_table = dynamodb.Table('geonames_cache')
    r = ddb_table.scan(ProjectionExpression='#n,lat,lng', ExpressionAttributeNames = {'#n': 'name'})
    places = r['Items']
    m2 = []
    for member in members:
        pc = member.get('postcode', None)
        if pc is None:
            m2.append(member)
        else:
            pc = f'{pc}'.strip()
            n = [p for p in places if p['name'] == pc]
            if len(n) == 0:
                loc = findnet(pc)
                if loc is None:
                    m2.append(member)
                else:
                    m2.append({**member, 'proximity': distance(loc, lng, lat)})
            else:
                m2.append({**member, 'proximity': distance(n[0], lng, lat)})
    return m2

def distance2(p, lng, lat): 
    place = f'{p}'.strip()
    try:
        ll = find()
        if ll is not None:
            return distance(ll, lng, lat)
    except Exception as e:
        print(f'error [{p}]', e)
    return 9999.0

def addproximity2(members, lng, lat):
    return [{**m, 'proximity': distance2(m['postcode'], lng, lat)} for m in members]