import requests
import json
from pyproj import Transformer

key = '' # TODO get from SSM

def find(place):
    r = requests.get('https://api.os.uk/search/names/v1/find', headers={'key': key}, params={'query': place, 'maxresults': 1})
    if r.ok:
        answer = r.json()
        entry = answer['results'][0]['GAZETTEER_ENTRY']
        ll = Transformer.from_crs("epsg:27700", "epsg:4326").transform(entry['GEOMETRY_X'], entry['GEOMETRY_Y'])
        return { 'place': place, 'latitude': ll[0], 'longitude': ll[1] }
