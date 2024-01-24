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
    ddb_table = dynamodb.Table('geonames_cache')
    r = ddb_table.get_item(Key={ 'name': place })
    if 'Item' in r:
      item = r['Item']
      return { 'place': place, 'latitude': item['lat'], 'longitude': item['lng'] }
    r = requests.get('https://api.os.uk/search/names/v1/find', headers={'key': key}, params={'query': place, 'maxresults': 1})
    if r.ok:
        answer = r.json()
        entry = answer['results'][0]['GAZETTEER_ENTRY']
        ll = OSGB36toWGS84(entry['GEOMETRY_X'], entry['GEOMETRY_Y'])
        data = { 'name': place, 'lat': ll[0], 'lng': ll[1] }
        ddb_table.put_item(Item={**data, 'timestamp':  int(datetime.utcnow().timestamp()) + 86400 })
        return { 'place': place, 'latitude': data['lat'], 'longitude': data['lng'] }

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))

def distance(place, lat, lng):
    ll = find(place)
    d = haversine(ll['longitude'], ll['latitude'], lng, lat)
    return float(int(10*d)/10)
