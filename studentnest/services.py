import requests
from django.conf import settings

def get_coordinates(street, city, state):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': street+city+state, 'key': settings.GOOGLE_GEOCODE_KEY}
    r = requests.get(url, params=params)
    result = r.json()
    if result['status'] != "OK" or len(result['results']) < 1:
        return None
    coordinates = {'latitude':result['results'][0]['geometry']['location']['lat'],'longitude':result['results'][0]['geometry']['location']['lng']}
    return coordinates
