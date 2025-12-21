"""Google Maps scraper using Playwright (free alternative to Apify)."""
import asyncio
import json
from typing import List, Dict, Optional
from pathlib import Path
import time

try:
    from playwright.async_api import async_playwright, Page
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    print("Then run: playwright install")

from config.settings import MAX_PLACES, MAX_REVIEWS_PER_PLACE, SCRAPER_TIMEOUT
from config.logger import setup_logging

logger = setup_logging('scraper')


class GoogleMapsScraper:
    """Scrape Google Maps reviews without Apify dependency."""
    
    def __init__(self, headless: bool = True):
        """Initialize scraper."""
        self.headless = headless
        self.timeout = SCRAPER_TIMEOUT * 1000  # Convert to milliseconds
        
    async def scrape_reviews(
        self,
        search_term: str,
        location: str,
        max_places: int = MAX_PLACES,
        max_reviews: int = MAX_REVIEWS_PER_PLACE
    ) -> Optional[List[Dict]]:
        """
        Scrape Google Maps reviews for a search term.
        
        Args:
            search_term: What to search for (e.g., "Dosa")
            location: Location (e.g., "Bengaluru")
            max_places: Maximum places to scrape
            max_reviews: Maximum reviews per place
            
        Returns:
            List of place data with reviews or None on error
        """
        logger.info(f"Starting scrape for '{search_term}' in '{location}'")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                
                # Set viewport
                await page.set_viewport_size({"width": 1280, "height": 720})
                
                try:
                    # Navigate to Google Maps
                    search_query = f"best {search_term} in {location}"
                    google_maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
                    
                    logger.info(f"Navigating to: {google_maps_url}")
                    await page.goto(google_maps_url, wait_until='networkidle')
                    await page.wait_for_timeout(2000)
                    
                    places = []
                    
                    # Get list of places
                    try:
                        place_cards = await page.query_selector_all('[role="button"]')
                        logger.info(f"Found {len(place_cards)} place cards")
                        
                        for idx, card in enumerate(place_cards[:max_places]):
                            try:
                                # Click on place card
                                await card.click()
                                await page.wait_for_timeout(1000)
                                
                                # Extract place information
                                place_data = await self._extract_place_info(page, max_reviews)
                                if place_data:
                                    places.append(place_data)
                                    logger.info(f"Scraped {idx + 1}/{min(max_places, len(place_cards))}: {place_data.get('name', 'Unknown')}")
                                
                            except Exception as e:
                                logger.warning(f"Error scraping place {idx}: {e}")
                                continue
                    
                    except Exception as e:
                        logger.error(f"Error finding places: {e}")
                    
                    logger.info(f"Successfully scraped {len(places)} places")
                    return places if places else None
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return None
    
    async def _extract_place_info(self, page: Page, max_reviews: int) -> Optional[Dict]:
        """Extract information about a place."""
        try:
            place_info = {
                'name': None,
                'rating': None,
                'review_count': 0,
                'address': None,
                'type': None,
                'reviews': [],
                'url': page.url
            }
            
            # Try to get place name
            try:
                name_element = await page.query_selector('h1')
                if name_element:
                    place_info['name'] = await name_element.text_content()
            except:
                pass
            
            # Try to get rating and review count
            try:
                rating_text = await page.text_content('[aria-label*="stars"]')
                if rating_text:
                    parts = rating_text.split()
                    if parts:
                        place_info['rating'] = float(parts[0])
                        if len(parts) > 1:
                            place_info['review_count'] = int(parts[1].replace(',', ''))
            except:
                pass
            
            # Try to get address
            try:
                address_element = await page.query_selector('[data-tooltip="Copy address"]')
                if address_element:
                    place_info['address'] = await address_element.text_content()
            except:
                pass
            
            # Try to get reviews
            try:
                review_elements = await page.query_selector_all('[data-review-id]')
                for review_elem in review_elements[:max_reviews]:
                    try:
                        review_text = await review_elem.text_content()
                        place_info['reviews'].append({
                            'text': review_text[:500],  # First 500 chars
                            'full_text': review_text
                        })
                    except:
                        continue
            except:
                pass
            
            return place_info if place_info['name'] else None
            
        except Exception as e:
            logger.error(f"Error extracting place info: {e}")
            return None
    
    def scrape_reviews_sync(
        self,
        search_term: str,
        location: str,
        max_places: int = MAX_PLACES,
        max_reviews: int = MAX_REVIEWS_PER_PLACE
    ) -> Optional[List[Dict]]:
        """Synchronous wrapper for scraping."""
        try:
            return asyncio.run(
                self.scrape_reviews(search_term, location, max_places, max_reviews)
            )
        except Exception as e:
            logger.error(f"Sync scraping failed: {e}")
            return None


async def scrape_google_maps_reviews(
    search_terms: List[str],
    location: str,
    max_places: int = MAX_PLACES,
    max_reviews: int = MAX_REVIEWS_PER_PLACE
) -> Optional[List[Dict]]:
    """
    Main function to scrape Google Maps reviews.
    
    Args:
        search_terms: List of search terms
        location: Location to search in
        max_places: Maximum places per search term
        max_reviews: Maximum reviews per place
        
    Returns:
        Combined list of places with reviews
    """
    scraper = GoogleMapsScraper()
    all_results = []
    
    for search_term in search_terms:
        logger.info(f"Processing search term: {search_term}")
        results = await scraper.scrape_reviews(search_term, location, max_places, max_reviews)
        if results:
            all_results.extend(results)
    
    return all_results if all_results else None


def scrape_google_maps_reviews_sync(
    search_terms: List[str],
    location: str,
    max_places: int = MAX_PLACES,
    max_reviews: int = MAX_REVIEWS_PER_PLACE
) -> Optional[List[Dict]]:
    """Synchronous version of scrape_google_maps_reviews."""
    try:
        return asyncio.run(
            scrape_google_maps_reviews(search_terms, location, max_places, max_reviews)
        )
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return None