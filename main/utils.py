import googlemaps
from django.conf import settings

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

def get_route(origin, destination):
    directions = gmaps.directions(origin, destination)
    # Process and return the route details
    return directions
