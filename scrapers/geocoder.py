"""
Geocoder using Nominatim (OpenStreetMap) — completely free, no API key required.
Respects the Nominatim usage policy: max 1 request/second, must include User-Agent.
Works globally — no country restriction.
"""

import time
import requests
from typing import Tuple, Optional
from config.logger import setup_logging

logger = setup_logging('geocoder')

# Fallback coordinates for common cities worldwide (used only if Nominatim fails)
CITY_COORDS = {
    # India
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "lucknow": (26.8467, 80.9462),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "kochi": (9.9312, 76.2673),
    # Global
    "new york": (40.7128, -74.0060),
    "new york city": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "tokyo": (35.6762, 139.6503),
    "beijing": (39.9042, 116.4074),
    "shanghai": (31.2304, 121.4737),
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
    "sydney": (-33.8688, 151.2093),
    "melbourne": (-37.8136, 144.9631),
    "toronto": (43.6532, -79.3832),
    "berlin": (52.5200, 13.4050),
    "madrid": (40.4168, -3.7038),
    "rome": (41.9028, 12.4964),
    "amsterdam": (52.3676, 4.9041),
    "bangkok": (13.7563, 100.5018),
    "seoul": (37.5665, 126.9780),
    "hong kong": (22.3193, 114.1694),
    "istanbul": (41.0082, 28.9784),
    "cairo": (30.0444, 31.2357),
    "nairobi": (-1.2921, 36.8219),
    "johannesburg": (-26.2041, 28.0473),
    "mexico city": (19.4326, -99.1332),
    "sao paulo": (-23.5505, -46.6333),
    "buenos aires": (-34.6037, -58.3816),
    "moscow": (55.7558, 37.6173),
    "kuala lumpur": (3.1390, 101.6869),
    "jakarta": (-6.2088, 106.8456),
}

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_USER_AGENT = "ReviewNexus/1.0 (educational project)"
_RATE_LIMIT_SECS = 1.1

_last_request_time: float = 0.0


def _rate_limit() -> None:
    """Ensure we don't exceed Nominatim's 1 req/sec policy."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _RATE_LIMIT_SECS:
        time.sleep(_RATE_LIMIT_SECS - elapsed)
    _last_request_time = time.time()


def get_city_fallback(location: str) -> Tuple[float, float]:
    import random
    
    loc_lower = location.lower()
    base_coords = (20.5937, 78.9629)  # centre of world (India) as last resort
    for key, coords in CITY_COORDS.items():
        if key in loc_lower:
            base_coords = coords
            break
    
    # Try Nominatim for the city name itself (global, no country filter)
    try:
        _rate_limit()
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": _USER_AGENT}
        resp = requests.get(_NOMINATIM_URL, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
    
    # Add random jitter (~4km radius) so markers don't stack on top of each other
    jitter_lat = random.uniform(-0.03, 0.03)
    jitter_lng = random.uniform(-0.03, 0.03)
    return (base_coords[0] + jitter_lat, base_coords[1] + jitter_lng)


def geocode_address(address: str, city: str, timeout: int = 5) -> Tuple[float, float]:
    """
    Geocode a restaurant address using Nominatim (global, no country restriction).
    Returns (latitude, longitude). Falls back to city center on failure.
    """
    if not address or address.strip() == city.strip():
        return get_city_fallback(city)

    clean_address = address.strip()
    if clean_address.lower().startswith("address:"):
        clean_address = clean_address[8:].strip()

    try:
        _rate_limit()
        params = {
            "q": f"{clean_address}, {city}",
            "format": "json",
            "limit": 1,
            "addressdetails": 0,
            # No countrycodes filter — works globally
        }
        headers = {"User-Agent": _USER_AGENT}
        resp = requests.get(_NOMINATIM_URL, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            logger.debug(f"Geocoded '{clean_address}' to ({lat:.4f}, {lon:.4f})")
            return (lat, lon)
    except Exception as e:
        logger.debug(f"Nominatim geocoding failed for '{clean_address}': {e}")

    return get_city_fallback(city)


def geocode_batch(
    places: list,
    city: str,
    address_key: str = "address",
    lat_key: str = "latitude",
    lng_key: str = "longitude",
) -> list:
    """
    Geocode a list of place dicts in-place.
    Only geocodes entries where lat/lng are 0 or missing.
    """
    need_geocoding = [p for p in places if not p.get(lat_key) or p.get(lat_key) == 0]
    logger.info(f"Geocoding {len(need_geocoding)}/{len(places)} places via Nominatim...")

    for place in need_geocoding:
        address = place.get(address_key, city)
        lat, lng = geocode_address(address, city)
        place[lat_key] = lat
        place[lng_key] = lng

    return places
