import json
import math
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .sentiment_analyzer import get_sentiment_for_reviews 
from config.settings import DATA_DIR

def _generate_google_maps_url(name: str, address: str) -> str:
    query = f"{name} {address}".strip()
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

def _validate_place_data(place: Dict) -> bool:
    if not isinstance(place, dict):
        return False
    name = place.get('name') or place.get('title')
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        return False
    return True

def _process_place(place: Dict, city: str) -> Optional[Dict]:
    if not _validate_place_data(place):
        return None
    
    title = (place.get('name') or place.get('title', 'N/A')).strip()
    avg_rating = float(place.get('rating') or place.get('totalScore', 0))
    review_count = int(place.get('review_count') or place.get('reviewsCount', 0))
    category = (place.get('category') or place.get('categoryName', 'Restaurant')).strip()
    address = (place.get('address', city)).strip()
    reviews_list = place.get('reviews', [])
    latitude = float(place.get('latitude', 0))
    longitude = float(place.get('longitude', 0))
    
    if not isinstance(reviews_list, list):
        reviews_list = []
    
    sentiment_score = get_sentiment_for_reviews(reviews_list)
    
    base_score = 0
    if review_count > 0:
        base_score = avg_rating * math.log10(review_count + 1)
    final_score = base_score * (1 + sentiment_score)
    
    url = _generate_google_maps_url(title, address)
    
    return {
        "name": title,
        "category": category,
        "avg_rating": round(avg_rating, 1),
        "reviews": review_count,
        "sentiment": f"{sentiment_score:.2f}",
        "score": round(final_score, 2),
        "address": address,
        "url": url,
        "latitude": latitude,
        "longitude": longitude
    }

def analyze_and_rank(data_filename: str, dish: str, city: str) -> None:
    try:
        with open(data_filename, 'r', encoding='utf-8') as f:
            places = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading or parsing {data_filename}: {e}")
        return

    if not places or not isinstance(places, list):
        print("No places to analyze.")
        return

    print(f"Analyzing {len(places)} places for '{dish}' in '{city}'...")
    
    ranked_list = []
    max_workers = min(4, len(places))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_place, place, city): i for i, place in enumerate(places)}
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result()
                if result:
                    ranked_list.append(result)
                    print(f"  -> Processed {len(ranked_list)}/{len(places)}: {result['name']}")
            except Exception as e:
                print(f"  Error processing place {idx}: {e}")

    if not ranked_list:
        print("No valid places found after analysis.")
        return

    ranked_list.sort(key=lambda x: x['score'], reverse=True)

    console = Console()
    table_title = f"Top Rated '{dish.title()}' in {city.title()}"
    table = Table(title=table_title, show_header=True, header_style="bold cyan")

    table.add_column("Rank", style="dim", width=4)
    table.add_column("Name", width=30)
    table.add_column("Category")
    table.add_column("Avg Rating", justify="center")
    table.add_column("Reviews", justify="center")
    table.add_column("Sentiment", justify="center")
    table.add_column("Score", justify="center")
    
    for i, item in enumerate(ranked_list):
        table.add_row(
            f"{i+1}",
            item['name'],
            item['category'],
            str(item['avg_rating']),
            str(item['reviews']),
            str(item['sentiment']),
            f"{item['score']:.2f}"
        )
    
    console.print(table)

    try:
        df = pd.DataFrame(ranked_list)
        clean_dish = dish.replace(" ", "_").lower()
        clean_city = city.replace(" ", "_").lower()
        csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\nSuccessfully saved results to '{csv_filename}'")
    except Exception as e:
        print(f"\nError saving to CSV: {e}")