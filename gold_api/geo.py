import boto3
import requests
from bng_latlon import OSGB36toWGS84
from math import radians, sin, cos, asin, sqrt

ssm = boto3.client('ssm', config={'region_name': 'eu-west-1'})

r = ssm.get_parameter(Name='/OS/API_KEY')
key = r['Parameter']['Value']

def find(place):
    r = requests.get('https://api.os.uk/search/names/v1/find', headers={'key': key}, params={'query': place, 'maxresults': 1})
    if r.ok:
        answer = r.json()
        entry = answer['results'][0]['GAZETTEER_ENTRY']
        ll = OSGB36toWGS84(entry['GEOMETRY_X'], entry['GEOMETRY_Y'])
        return { 'place': place, 'latitude': ll[0], 'longitude': ll[1] }

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))

def distance(place, lat, lng):
    ll = find(place)
    d = haversine(ll['longitude'], ll['latitude'], lng, lat)
    print(d)
    return d