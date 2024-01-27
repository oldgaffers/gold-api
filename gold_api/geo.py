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

def find(place):
    if place is None:
        return None
    p = f'{place}'.strip()
    if p == '':
        return None
    ddb_table = dynamodb.Table('geonames_cache')
    r = ddb_table.get_item(Key={ 'name': p })
    if 'Item' in r:
      item = r['Item']
      data = { 'place': p, 'latitude': float(item['lat']), 'longitude': float(item['lng']) }
      return data
    r = requests.get('https://api.os.uk/search/names/v1/find', headers={'key': key}, params={'query': place, 'maxresults': 1})
    if r.ok:
        answer = r.json()
        entry = answer['results'][0]['GAZETTEER_ENTRY']
        lat, lng = OSGB36toWGS84(entry['GEOMETRY_X'], entry['GEOMETRY_Y'])
        data = { 'name': p, 'lat': f'{lat}', 'lng': f'{lng}' }
        item = {**data, 'timestamp':  int(datetime.utcnow().timestamp()) + 86400 }
        ddb_table.put_item(Item=item)
        result = { 'place': p, 'latitude': lat, 'longitude': lng }
        return result
    else:
        print('error', r)

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))

def distance(place, lng, lat): 
    try:
        ll = find(place)
        if ll is not None:
            d = haversine(ll['longitude'], ll['latitude'], lng, lat)
            d = d / 1.852
            d = float(int(10*d)/10)
            return d
    except Exception as e:
        print(f'error [{place}]', e)
    return 9999.0
