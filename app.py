import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'nearbyBusinesses')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'trafficLights')))
from fastapi import FastAPI
from climate.open_meteo import get_climate_data
from nearbyBusinesses.nearby_businesses import get_nearby_business_count
from trafficLights.nearby_traffic_lights import get_nearby_traffic_lights, filter_duplicate_locations
from speedLimits.speed_limits import get_nearest_roads_with_speed
from operationalHours.searchNearby import find_nearby_places


app = FastAPI()

@app.get("/climate")
def get_climate(lat: float, lon: float):
    """
    This endpoint takes latitude and longitude as query parameters,
    fetches climate data using the get_climate_data function,
    and returns the data as a JSON response.
    """
    climate_data = get_climate_data(lat, lon)
    if climate_data:
        return climate_data
    else:
        return {"error": "Could not retrieve climate data."}

@app.get("/nearby-businesses")
def get_nearby_businesses(lat: float, lon: float):
    """
    This endpoint takes latitude and longitude as query parameters,
    fetches nearby businesses data, and returns it as a JSON response.
    """
    nearby_businesses_data = get_nearby_business_count(lat, lon)
    if nearby_businesses_data:
        nearest_businesses = nearby_businesses_data.get('nearest_businesses', [])
        multiple_business_count = sum(1 for business in nearest_businesses if business['address'] == nearby_businesses_data['target_car_wash']['address'])
        output_row = {
            'Latitude': lat,
            'Longitude': lon,
            'car_wash_name': nearby_businesses_data['target_car_wash']['name'],
            'distance_from_original_location': nearby_businesses_data.get('distance', ''),
            'car_wash_address': nearby_businesses_data['target_car_wash']['address'],
            'nearest_business_name_1': nearest_businesses[0]['name'] if len(nearest_businesses) > 0 else '',
            'nearest_business_address_1': nearest_businesses[0]['address'] if len(nearest_businesses) > 0 else '',
            'distance_car_wash_nearest_business_1': nearby_businesses_data.get('distance_car_wash_nearest_business_1', ''),
            'nearest_business_name_2': nearest_businesses[1]['name'] if len(nearest_businesses) > 1 else '',
            'nearest_business_address_2': nearest_businesses[1]['address'] if len(nearest_businesses) > 1 else '',
            'distance_car_wash_nearest_business_2': nearby_businesses_data.get('distance_car_wash_nearest_business_2', ''),
            'nearest_business_name_3': nearest_businesses[2]['name'] if len(nearest_businesses) > 2 else '',
            'nearest_business_address_3': nearest_businesses[2]['address'] if len(nearest_businesses) > 2 else '',
            'distance_car_wash_nearest_business_3': nearby_businesses_data.get('distance_car_wash_nearest_business_3', ''),
            'nearest_business_name_4': nearest_businesses[3]['name'] if len(nearest_businesses) > 3 else '',
            'nearest_business_address_4': nearest_businesses[3]['address'] if len(nearest_businesses) > 3 else '',
            'distance_car_wash_nearest_business_4': nearby_businesses_data.get('distance_car_wash_nearest_business_4', ''),
            'nearest_business_name_5': nearest_businesses[4]['name'] if len(nearest_businesses) > 4 else '',
            'nearest_business_address_5': nearest_businesses[4]['address'] if len(nearest_businesses) > 4 else '',
            'distance_car_wash_nearest_business_5': nearby_businesses_data.get('distance_car_wash_nearest_business_5', ''),
            'multiple_business_count': multiple_business_count
        }
        return output_row
    else:
        return {"error": "Could not retrieve nearby businesses data."}

@app.get("/traffic-lights")
def get_traffic_lights(lat: float, lon: float):
    """
    This endpoint takes latitude and longitude as query parameters,
    fetches nearby traffic lights data, and returns it as a JSON response.
    """
    sorted_traffic_lights = get_nearby_traffic_lights(lat, lon)
    unique_traffic_lights = filter_duplicate_locations(sorted_traffic_lights)
    output_row = {
        'Latitude': lat,
        'Longitude': lon,
        'nearby_traffic_lights_count': len(unique_traffic_lights)
    }
    for i in range(10):
        if i < len(unique_traffic_lights):
            output_row[f'distance_nearest_traffic_light_{i+1}'] = unique_traffic_lights[i]['distance_miles']
        else:
            output_row[f'distance_nearest_traffic_light_{i+1}'] = None
    return output_row

@app.get("/speed-limits")
def get_speed_limits(lat: float, lon: float, radius: int = 3219):
    """
    This endpoint takes latitude and longitude as query parameters,
    fetches speed limits of nearby roads, and returns it as a JSON response.
    """
    nearest_roads = get_nearest_roads_with_speed(lat, lon, radius)
    if nearest_roads:
        closest_roads = {}
        unique_roads = []
        for road in nearest_roads:
            road_name = road['name']
            if road_name not in closest_roads:
                closest_roads[road_name] = {'id': road['id'], 'distance': road['distance'], 'maxspeed': road['maxspeed']}
                unique_roads.append(road)
            else:
                if road['distance'] < closest_roads[road_name]['distance']:
                    closest_roads[road_name] = {'id': road['id'], 'distance': road['distance'], 'maxspeed': road['maxspeed']}
        output_row = {
            'Latitude': lat,
            'Longitude': lon,
        }
        for i in range(min(5, len(unique_roads))):
            output_row[f'nearestroad_{i+1}_name'] = unique_roads[i]['name']
            output_row[f'distance_nearestroad_{i+1}'] = unique_roads[i]['distance']
            output_row[f'nearestroad_{i+1}_maxspeed'] = unique_roads[i].get('maxspeed', 'N/A')
        for i in range(len(unique_roads), 5):
            output_row[f'nearestroad_{i+1}_name'] = None
            output_row[f'distance_nearestroad_{i+1}'] = None
            output_row[f'nearestroad_{i+1}_maxspeed'] = None
        return output_row
    else:
        return {"error": "Could not retrieve speed limits data."}

@app.get("/operational-hours")
def get_operational_hours(lat: float, lon: float, radius: int = 3219, place_type: str = "car_wash", max_results: int = 1):
    """
    This endpoint takes latitude and longitude as query parameters,
    fetches operational hours of a nearby place, and returns it as a JSON response.
    """
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    if not API_KEY:
        return {"error": "GOOGLE_MAPS_API_KEY not set"}
    results = find_nearby_places(
        API_KEY,
        lat,
        lon,
        radius_miles=radius/1609.34,
        included_types=[place_type],
        max_results=max_results,
        rank_preference="DISTANCE"
    )
    if results and "places" in results and results["places"]:
        nearest_place = results["places"][0]
        output_row = {
            'Latitude': lat,
            'Longitude': lon,
            'display_name': nearest_place.get("displayName", {}).get("text", "N/A"),
            'actual_latitude': nearest_place.get("location", {}).get("latitude", "N/A"),
            'actual_longitude': nearest_place.get("location", {}).get("longitude", "N/A"),
            'rating': nearest_place.get("rating", "N/A"),
            'rating_count': nearest_place.get("userRatingCount", "N/A"),
            'business_status': nearest_place.get("businessStatus", "N/A")
        }
        opening_hours = nearest_place.get("regularOpeningHours", {})
        weekday_descriptions = opening_hours.get("weekdayDescriptions", [])
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        days_hours = {f"{day}_operational_hours": "N/A" for day in days}

        if weekday_descriptions:
            for desc in weekday_descriptions:
                cleaned_desc = desc.replace('\u202f', ' ').replace('\u2009', ' ')
                parts = cleaned_desc.split(':', 1)
                if len(parts) == 2:
                    day_name = parts[0].strip().lower()
                    hours = parts[1].strip()
                    column_name = f"{day_name}_operational_hours"
                    if column_name in days_hours:
                        days_hours[column_name] = hours
        output_row.update(days_hours)
        return output_row
    else:
        return {"error": "Could not retrieve operational hours data."}
