from apps.api.seeds.geo_constants import find_nearest_poi

def normalize_address(latitude: float, longitude: float, user_provided_address: str = None) -> str:
    """Return standardized street address or near-POI descriptor."""
    if user_provided_address and len(user_provided_address.strip()) > 3:
        return user_provided_address.strip()

    poi_name, distance = find_nearest_poi(latitude, longitude)
    if poi_name and distance <= 150.0:
        return f"Near {poi_name} (~{int(distance)}m), Ward 12"

    return f"Ward 12 Municipal Corridor [Lat: {latitude:.4f}, Lon: {longitude:.4f}]"

def round_coordinates_for_public(latitude: float, longitude: float) -> tuple[float, float]:
    """Round coordinates to 3 decimal places (~100m) for public citizen view privacy."""
    return round(latitude, 3), round(longitude, 3)

