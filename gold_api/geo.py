import requests
from bng_latlon import OSGB36toWGS84
import boto3

ssm = boto3.client('ssm')

r = ssm.get_parameter(Name='/OS/API_KEY')
key = r['Parameter']['Value']

def find(place):
    r = requests.get('https://api.os.uk/search/names/v1/find', headers={'key': key}, params={'query': place, 'maxresults': 1})
    if r.ok:
        answer = r.json()
        entry = answer['results'][0]['GAZETTEER_ENTRY']
        ll = OSGB36toWGS84(entry['GEOMETRY_X'], entry['GEOMETRY_Y'])
        return { 'place': place, 'latitude': ll[0], 'longitude': ll[1] }
