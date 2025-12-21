#!/usr/bin/env python
"""Test script to verify the scraper works."""

import sys
sys.path.insert(0, '/foodrank')

from scrapers.google_maps_scraper import scrape_google_maps_reviews_sync
import json

print("\n" + "="*60)
print("Testing Google Maps Web Scraper")
print("="*60 + "\n")

# Test parameters
search_terms = ["best dosa restaurants"]
location = "Bengaluru, India"

print(f"Searching for: {search_terms}")
print(f"Location: {location}\n")

print("Attempting to scrape real data from Google Maps...")
print("(This may take 30-60 seconds)\n")

try:
    results = scrape_google_maps_reviews_sync(
        search_terms=search_terms,
        location=location,
        max_places=5,
        max_reviews=3
    )
    
    if results:
        print(f"\n[SUCCESS] Scraped {len(results)} restaurants:\n")
        for i, place in enumerate(results, 1):
            print(f"{i}. {place.get('name', 'N/A')}")
            print(f"   Rating: {place.get('rating', 'N/A')} stars")
            print(f"   Reviews: {place.get('review_count', 0)} reviews")
            print(f"   Address: {place.get('address', 'N/A')}")
            print()
        
        print(f"Full result (JSON):")
        print(json.dumps(results, indent=2))
    else:
        print("[ERROR] Scraping returned no results - using fallback mock data")
        
except Exception as e:
    print(f"[ERROR] Error during scraping: {e}")
    import traceback
    traceback.print_exc()
