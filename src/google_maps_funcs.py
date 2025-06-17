import googlemaps
from dotenv import load_dotenv
import os
import hashlib
import json

_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)


def _matrix_cache_key(origins, destinations, mode):
    key_data = json.dumps(
        {"origins": origins, "destinations": destinations, "mode": mode}, sort_keys=True
    )
    return hashlib.sha256(key_data.encode("utf-8")).hexdigest()


def _matrix_cache_path(origins, destinations, mode):
    key = _matrix_cache_key(origins, destinations, mode)
    return os.path.join(_CACHE_DIR, f"matrix_{key}.json")


def get_distance_matrix(origins, destinations, mode="driving"):
    """
    Load Google API key from .env and return distance matrix. Uses file cache in .cache/.

    Parameters:
        origins (list of str): Origin addresses or "lat,lng".
        destinations (list of str): Destination addresses or "lat,lng".
        mode (str): One of 'driving', 'walking', 'bicycling', 'transit'.

    Returns:
        dict: {origin: {destination: {'distance': ..., 'duration': ...}}}
    """
    cache_path = _matrix_cache_path(origins, destinations, mode)
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    load_dotenv()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in .env")

    gmaps = googlemaps.Client(key=api_key)
    matrix_response = gmaps.distance_matrix(origins, destinations, mode=mode)

    result = {}
    for i, origin in enumerate(matrix_response["origin_addresses"]):
        result[origin] = {}
        for j, destination in enumerate(matrix_response["destination_addresses"]):
            element = matrix_response["rows"][i]["elements"][j]
            if element["status"] == "OK":
                result[origin][destination] = {
                    "distance": element["distance"]["text"],
                    "duration": element["duration"]["text"],
                }
            else:
                result[origin][destination] = {"error": element["status"]}
    with open(cache_path, "w") as f:
        json.dump(result, f)
    return result


def get_distance_matrix_batched(origins, destinations, mode="driving", batch_size=25):
    """
    Wrapper for get_distance_matrix that batches requests to max 25x25 and only computes the upper triangular matrix (one-way directions).

    Parameters:
        origins (list of str): Origin addresses or "lat,lng".
        destinations (list of str): Destination addresses or "lat,lng".
        mode (str): Travel mode.
        batch_size (int): Max batch size for API call (default 25).

    Returns:
        dict: {origin: {destination: {'distance': ..., 'duration': ...}}}
    """
    n = len(origins)
    m = len(destinations)
    result = {}
    for i in range(n):
        # Only consider destinations with index > i for upper triangle
        dest_indices = [j for j in range(i + 1, m)]
        if not dest_indices:
            continue
        # Batch destinations for this origin
        for k in range(0, len(dest_indices), batch_size):
            batch_dest_indices = dest_indices[k : k + batch_size]
            batch_destinations = [destinations[j] for j in batch_dest_indices]
            batch_origins = [origins[i]]
            batch_result = get_distance_matrix(batch_origins, batch_destinations, mode)
            origin_addr = list(batch_result.keys())[0]
            if origin_addr not in result:
                result[origin_addr] = {}
            for dest_addr in batch_result[origin_addr]:
                result[origin_addr][dest_addr] = batch_result[origin_addr][dest_addr]
    return result


def get_coordinates(locations):
    """
    Given a list of location names/addresses, return their latitude and longitude using Google Maps Geocoding API.

    Parameters:
        locations (list of str): List of addresses or place names.

    Returns:
        dict: {location: {'lat': ..., 'lng': ...}} or {location: {'error': ...}}
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in .env")

    gmaps = googlemaps.Client(key=api_key)
    result = {}
    for location in locations:
        geocode_result = gmaps.geocode(location)
        if geocode_result and "geometry" in geocode_result[0]:
            latlng = geocode_result[0]["geometry"]["location"]
            result[location] = {"lat": latlng["lat"], "lng": latlng["lng"]}
        else:
            result[location] = {"error": "Not found"}
    return result


if __name__ == "__main__":
    # Example usage

    origins = ["Honningsvåg, Nordkapp, Finnmark"]
    destinations = ["Mehamn, Gamvik, Finnmark"]
    mode = "driving"

    try:
        distance_matrix = get_distance_matrix(origins, destinations, mode)
        print(distance_matrix)
    except Exception as e:
        print(f"Error: {e}")
