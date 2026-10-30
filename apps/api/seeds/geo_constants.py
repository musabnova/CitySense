import math

# Geographic Center for Ward 12 Municipal District
WARD_12_CENTER = {"latitude": 12.9716, "longitude": 77.5946}
WARD_12_RADIUS_METERS = 1500.0 # 1.5 km municipal operational radius

# Critical Sensitive Points of Interest (POIs) used for proximity risk scoring
ANCHOR_POIS = {
    "st_jude_school": {
        "name": "St. Jude Primary School",
        "category": "Education / School Zone",
        "latitude": 12.9725,
        "longitude": 77.5950,
        "sensitivity_buffer_meters": 75.0,
    },
    "city_central_hospital": {
        "name": "City Central Hospital",
        "category": "Healthcare / Emergency Access",
        "latitude": 12.9705,
        "longitude": 77.5935,
        "sensitivity_buffer_meters": 75.0,
    },
    "metro_transit_junction": {
        "name": "Metro Transit Junction",
        "category": "Public Transit / High Footfall",
        "latitude": 12.9730,
        "longitude": 77.5970,
        "sensitivity_buffer_meters": 75.0,
    },
}

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in meters using the Haversine formula."""
    R = 6371000.0 # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def find_nearest_poi(lat: float, lon: float) -> tuple[str, float]:
    """Find the nearest critical POI and return its name and distance in meters."""
    nearest_poi = None
    min_distance = float("inf")
    for poi_id, poi_data in ANCHOR_POIS.items():
        dist = calculate_haversine_distance(lat, lon, poi_data["latitude"], poi_data["longitude"])
        if dist < min_distance:
            min_distance = dist
            nearest_poi = poi_data["name"]
    return nearest_poi, min_distance

