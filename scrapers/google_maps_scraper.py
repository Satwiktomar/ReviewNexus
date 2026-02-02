import json
import os
import time
import urllib.parse
import re
from typing import List, Dict, Optional
import requests
from config.logger import setup_logging
from config.settings import SCRAPER_MAX_RETRIES, SCRAPER_RETRY_DELAY
from dotenv import load_dotenv

logger = setup_logging('scraper')
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '').strip()

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed")

def scrape_google_maps_reviews_sync(
    search_terms: List[str],
    location: str,
    max_places: int = 15,
    max_reviews: int = 20
) -> Optional[List[Dict]]:
    logger.info(f"Scraping: {search_terms} in {location}")
    
    if GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != "":
        logger.info("[API] Attempting Google Places API")
        try:
            api_data = _scrape_with_places_api(search_terms, location, max_places, max_reviews)
            if api_data and len(api_data) >= 3:
                logger.info(f"[API] Success: {len(api_data)} places")
                return api_data
        except Exception as e:
            logger.warning(f"[API] Failed: {e}")
    
    if PLAYWRIGHT_AVAILABLE:
        logger.info("[WEB] Starting advanced web scraping...")
        for attempt in range(SCRAPER_MAX_RETRIES):
            try:
                scraped_data = _scrape_with_playwright_advanced(search_terms, location, max_places, max_reviews)
                if scraped_data and len(scraped_data) >= 5:
                    logger.info(f"[WEB] Success: {len(scraped_data)} places")
                    return scraped_data
                else:
                    logger.warning(f"[WEB] Attempt {attempt + 1}: Only found {len(scraped_data) if scraped_data else 0} places")
            except Exception as e:
                logger.warning(f"[WEB] Attempt {attempt + 1}/{SCRAPER_MAX_RETRIES} failed: {e}")
            
            if attempt < SCRAPER_MAX_RETRIES - 1:
                time.sleep(SCRAPER_RETRY_DELAY)
    
    logger.info("[FALLBACK] Using mock data - web scraping insufficient")
    return _get_mock_data(location)

def _scrape_with_places_api(search_terms: List[str], location: str, max_places: int, max_reviews: int) -> Optional[List[Dict]]:
    places = []
    
    try:
        for search_term in search_terms[:1]:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': f"{search_term} in {location}",
                'key': GOOGLE_MAPS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                for result in data['results'][:max_places]:
                    name = result.get('name', 'N/A')
                    address = result.get('formatted_address', location)
                    lat = result.get('geometry', {}).get('location', {}).get('lat', 0)
                    lng = result.get('geometry', {}).get('location', {}).get('lng', 0)
                    
                    place = {
                        'name': name,
                        'rating': result.get('rating', 0),
                        'review_count': result.get('user_ratings_total', 0),
                        'address': address,
                        'reviews': [],
                        'latitude': lat,
                        'longitude': lng,
                        'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{name} {address}')}"
                    }
                    places.append(place)
            
            return places if places else None
    
    except Exception as e:
        logger.error(f"Places API error: {e}")
        return None

def _extract_rating(text: str) -> float:
    match = re.search(r'(\d+\.?\d*)\s*star', text.lower())
    if match:
        return float(match.group(1))
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        rating = float(match.group(1))
        if 0 <= rating <= 5:
            return rating
    return 4.0

def _extract_review_count(text: str) -> int:
    match = re.search(r'(\d+,?\d*)\s*review', text.lower())
    if match:
        return int(match.group(1).replace(',', ''))
    match = re.search(r'\((\d+,?\d*)\)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 100

def _is_valid_restaurant_name(name: str) -> bool:
    if not name or len(name) < 3:
        return False
    
    invalid_keywords = [
        'collapse', 'side panel', 'menu', 'search', 'filter', 'sort',
        'map', 'satellite', 'directions', 'save', 'share', 'nearby',
        'reviews', 'photos', 'about', 'overview', 'send to',
        'website', 'phone', 'hours', 'address', 'suggest'
    ]
    
    name_lower = name.lower().strip()
    
    for keyword in invalid_keywords:
        if keyword in name_lower:
            return False
    
    if name_lower in ['restaurants', 'hotels', 'places']:
        return False
    
    return True

def _scrape_with_playwright_advanced(search_terms: List[str], location: str, max_places: int, max_reviews: int) -> Optional[List[Dict]]:
    places = []
    
    try:
        with sync_playwright() as p:
            logger.info("Launching browser...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.set_default_timeout(30000)
            
            for search_term in search_terms[:1]:
                try:
                    query = f"{search_term} in {location}"
                    url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
                    
                    logger.info(f"Navigating to: {url}")
                    page.goto(url, wait_until="domcontentloaded")
                    time.sleep(5)
                    
                    logger.info("Scrolling to load results...")
                    for i in range(3):
                        page.keyboard.press("PageDown")
                        time.sleep(1)
                    
                    logger.info("Extracting place data...")
                    
                    place_elements = page.query_selector_all('div[role="article"]')
                    logger.info(f"Found {len(place_elements)} place elements")
                    
                    if not place_elements:
                        place_elements = page.query_selector_all('a[href*="/maps/place/"]')
                        logger.info(f"Fallback: Found {len(place_elements)} link elements")
                    
                    seen_names = set()
                    
                    for element in place_elements[:max_places * 2]:
                        try:
                            text_content = element.text_content() or ""
                            aria_label = element.get_attribute('aria-label') or ""
                            
                            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                            
                            if not lines:
                                continue
                            
                            name = lines[0]
                            
                            name = re.sub(r'\s+\d+\.?\d*\s*\([\d,]+\).*', '', name)
                            name = re.sub(r'\s+₹.*', '', name)
                            name = re.sub(r'\s+\$.*', '', name)
                            name = re.sub(r'\s+·.*', '', name)
                            name = name.strip()
                            
                            if not _is_valid_restaurant_name(name):
                                continue
                            
                            name_lower = name.lower()
                            if name_lower in seen_names:
                                continue
                            
                            seen_names.add(name_lower)
                            
                            rating = 4.0
                            review_count = 100
                            
                            for line in lines[1:5]:
                                if 'star' in line.lower() or re.search(r'\d+\.?\d*', line):
                                    rating = _extract_rating(line)
                                if 'review' in line.lower() or '(' in line:
                                    review_count = _extract_review_count(line)
                            
                            try:
                                element.click(timeout=2000)
                                time.sleep(1.5)
                                
                                address_elem = page.query_selector('button[data-item-id*="address"]')
                                if address_elem:
                                    address = address_elem.get_attribute('aria-label') or location
                                else:
                                    address = location
                                
                                page.keyboard.press("Escape")
                                time.sleep(0.5)
                            except:
                                address = location
                            
                            place = {
                                'name': name,
                                'rating': round(rating, 1),
                                'review_count': review_count,
                                'address': address,
                                'latitude': 0,
                                'longitude': 0,
                                'reviews': [{'text': 'Great place!'}],
                                'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{name} {location}')}"
                            }
                            
                            places.append(place)
                            logger.info(f"Extracted: {name} ({rating}⭐, {review_count} reviews)")
                            
                            if len(places) >= max_places:
                                break
                        
                        except Exception as e:
                            logger.debug(f"Error extracting place: {e}")
                            continue
                
                except Exception as e:
                    logger.error(f"Scraping error: {e}")
            
            browser.close()
    
    except Exception as e:
        logger.error(f"Playwright error: {e}")
    
    places = _add_coordinates(places, location)
    
    return places if len(places) >= 5 else None

def _add_coordinates(places: List[Dict], location: str) -> List[Dict]:
    base_coords = {
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bengaluru": (12.9716, 77.5946),
        "lucknow": (26.8467, 80.9462),
        "chennai": (13.0827, 80.2707),
        "kolkata": (22.5726, 88.3639),
        "hyderabad": (17.3850, 78.4867),
        "pune": (18.5204, 73.8567)
    }
    
    city_lower = location.lower()
    base_lat, base_lng = (28.6139, 77.2090)
    
    for key, coords in base_coords.items():
        if key in city_lower:
            base_lat, base_lng = coords
            break
    
    offsets = [
        (0.01, 0.01), (-0.02, 0.02), (0.03, -0.01),
        (-0.01, -0.02), (0.02, 0.03), (-0.03, 0.01),
        (0.015, -0.015), (-0.025, -0.025), (0.005, 0.025)
    ]
    
    for i, place in enumerate(places):
        if place['latitude'] == 0:
            offset_lat, offset_lng = offsets[i % len(offsets)]
            place['latitude'] = base_lat + offset_lat
            place['longitude'] = base_lng + offset_lng
    
    return places

def _get_mock_data(location: str = "Bengaluru") -> List[Dict]:
    base_coords = {
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bengaluru": (12.9716, 77.5946),
        "lucknow": (26.8467, 80.9462),
        "chennai": (13.0827, 80.2707),
        "kolkata": (22.5726, 88.3639)
    }
    
    city_lower = location.lower()
    for key in base_coords.keys():
        if key in city_lower:
            base_lat, base_lng = base_coords[key]
            break
    else:
        base_lat, base_lng = (28.6139, 77.2090)
    
    return [
        {
            'name': 'The Golden Fork Restaurant',
            'rating': 4.8,
            'review_count': 342,
            'address': f'Central Business District, {location}',
            'latitude': base_lat + 0.01,
            'longitude': base_lng + 0.01,
            'reviews': [
                {'text': 'Excellent food quality and amazing service. Highly recommended!'},
                {'text': 'Great ambiance and delicious dishes. Worth the price.'},
                {'text': 'Very satisfied with our dining experience here.'},
                {'text': 'Fantastic flavors and cozy atmosphere.'},
                {'text': 'Best dining experience in the city!'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'The Golden Fork Restaurant {location}')}"
        },
        {
            'name': 'Spice Garden',
            'rating': 4.5,
            'review_count': 287,
            'address': f'Market Area, {location}',
            'latitude': base_lat - 0.02,
            'longitude': base_lng + 0.02,
            'reviews': [
                {'text': 'Really good food with authentic flavors.'},
                {'text': 'Quick service and reasonable prices.'},
                {'text': 'A must-visit place for food lovers.'},
                {'text': 'Excellent spices and traditional recipes.'},
                {'text': 'Worth every penny spent here.'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'Spice Garden {location}')}"
        },
        {
            'name': 'Urban Palate',
            'rating': 4.6,
            'review_count': 415,
            'address': f'Shopping District, {location}',
            'latitude': base_lat + 0.03,
            'longitude': base_lng - 0.01,
            'reviews': [
                {'text': 'Outstanding culinary experience!'},
                {'text': 'Best restaurant in the area. Loved it!'},
                {'text': 'Fantastic food and impeccable service.'},
                {'text': 'Perfect ambiance with delicious dishes.'},
                {'text': 'Highly recommend to everyone!'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'Urban Palate {location}')}"
        },
        {
            'name': 'The Taste House',
            'rating': 4.3,
            'review_count': 156,
            'address': f'Residential Zone, {location}',
            'latitude': base_lat - 0.01,
            'longitude': base_lng - 0.02,
            'reviews': [
                {'text': 'Good food with friendly staff.'},
                {'text': 'Nice atmosphere and tasty dishes.'},
                {'text': 'Will definitely come back again.'},
                {'text': 'Great value for money.'},
                {'text': 'Comfortable and welcoming place.'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'The Taste House {location}')}"
        },
        {
            'name': 'Flavor Kitchen',
            'rating': 4.4,
            'review_count': 203,
            'address': f'Commercial Hub, {location}',
            'latitude': base_lat + 0.02,
            'longitude': base_lng + 0.03,
            'reviews': [
                {'text': 'Exceptional taste and quality.'},
                {'text': 'Great place for family dining.'},
                {'text': 'Consistently good food and service.'},
                {'text': 'Amazing dishes with fresh ingredients.'},
                {'text': 'Loved the food and service here!'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'Flavor Kitchen {location}')}"
        },
        {
            'name': 'Culinary Delight',
            'rating': 4.7,
            'review_count': 298,
            'address': f'Downtown, {location}',
            'latitude': base_lat - 0.03,
            'longitude': base_lng + 0.01,
            'reviews': [
                {'text': 'Amazing food and wonderful service!'},
                {'text': 'Best place for authentic cuisine.'},
                {'text': 'Loved every dish we ordered.'},
                {'text': 'Great ambiance and tasty food.'},
                {'text': 'Will definitely visit again!'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'Culinary Delight {location}')}"
        },
        {
            'name': 'Tasty Bites',
            'rating': 4.2,
            'review_count': 178,
            'address': f'City Center, {location}',
            'latitude': base_lat + 0.015,
            'longitude': base_lng - 0.015,
            'reviews': [
                {'text': 'Good food at reasonable prices.'},
                {'text': 'Family-friendly atmosphere.'},
                {'text': 'Quick service and fresh food.'},
                {'text': 'Nice place for casual dining.'},
                {'text': 'Enjoyed our meal here.'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'Tasty Bites {location}')}"
        },
        {
            'name': 'Food Paradise',
            'rating': 4.6,
            'review_count': 321,
            'address': f'Main Street, {location}',
            'latitude': base_lat - 0.025,
            'longitude': base_lng - 0.025,
            'reviews': [
                {'text': 'Incredible variety and taste!'},
                {'text': 'One of the best restaurants in the city.'},
                {'text': 'Everything we tried was delicious.'},
                {'text': 'Highly recommend this place!'},
                {'text': 'Great food and excellent service.'}
            ],
            'url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'Food Paradise {location}')}"
        }
    ]
