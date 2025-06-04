import googlemaps
from dotenv import load_dotenv
import os

def get_distance_matrix(origins, destinations, mode='driving'):
    """
    Load Google API key from .env and return distance matrix.

    Parameters:
        origins (list of str): Origin addresses or "lat,lng".
        destinations (list of str): Destination addresses or "lat,lng".
        mode (str): One of 'driving', 'walking', 'bicycling', 'transit'.

    Returns:
        dict: {origin: {destination: {'distance': ..., 'duration': ...}}}
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in .env")

    gmaps = googlemaps.Client(key=api_key)
    matrix = gmaps.distance_matrix(origins, destinations, mode=mode)

    result = {}
    for i, origin in enumerate(matrix['origin_addresses']):
        result[origin] = {}
        for j, destination in enumerate(matrix['destination_addresses']):
            element = matrix['rows'][i]['elements'][j]
            if element['status'] == 'OK':
                result[origin][destination] = {
                    'distance': element['distance']['text'],
                    'duration': element['duration']['text'],
                }
            else:
                result[origin][destination] = {'error': element['status']}
    return result