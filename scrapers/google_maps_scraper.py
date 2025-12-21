
from apify_client import ApifyClient

def scrape_google_maps_reviews(api_token: str, search_terms: list, location: str, max_places: int):

    print("Initializing Apify Client...")
    client = ApifyClient(api_token)

    run_input = {
        "searchStringsArray": search_terms,
        "locationQuery": location, 
        "maxCrawledPlaces": max_places,
        "maxReviews": 20,
        "language": "en",
        "proxyConfig": { "useApifyProxy": True }
    }

    print(f"Starting Google Maps Scraper for '{search_terms[0]}'...")
    
    try:
        actor_run = client.actor("compass/crawler-google-places").call(run_input=run_input)
        print("Scraping finished. Fetching results...")

        items = []
        for item in client.dataset(actor_run["defaultDatasetId"]).iterate_items():
            items.append(item)
        

        return items

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None 