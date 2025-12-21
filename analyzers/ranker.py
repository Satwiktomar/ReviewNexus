
import json
import math
from pathlib import Path
from rich.console import Console
from rich.table import Table
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .sentiment_analyzer import get_sentiment_for_reviews 
from config.settings import DATA_DIR

def _process_place(place):
    """Process a single place (used for parallel processing)."""
    # Handle both old and new data formats
    title = place.get('name') or place.get('title', 'N/A')
    avg_rating = place.get('rating') or place.get('totalScore', 0)
    review_count = place.get('review_count') or place.get('reviewsCount', 0)
    category = place.get('category') or place.get('categoryName', 'N/A')
    address = place.get('address', 'N/A')
    reviews_list = place.get('reviews', [])
    
    # Run sentiment analysis (most expensive operation - parallelize this!)
    sentiment_score = get_sentiment_for_reviews(reviews_list)
    
    base_score = 0
    if review_count > 0:
        base_score = avg_rating * math.log10(review_count + 1)
    final_score = base_score * (1 + sentiment_score)
    
    return {
        "name": title, "category": category, "avg_rating": avg_rating,
        "reviews": review_count, "sentiment": f"{sentiment_score:.2f}",
        "score": round(final_score, 2), "address": address
    }

def analyze_and_rank(data_filename: str, dish: str, city: str):
    try:
        with open(data_filename, 'r', encoding='utf-8') as f:
            places = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading or parsing {data_filename}: {e}")
        return

    if not places:
        print("No places to analyze.")
        return

    print(f"Analyzing {len(places)} places for '{dish}' in '{city}'...")
    
    # PARALLEL PROCESSING - process multiple places simultaneously
    ranked_list = []
    max_workers = min(4, len(places))  # Use up to 4 threads
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_place, place): i for i, place in enumerate(places)}
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result()
                ranked_list.append(result)
                print(f"  -> Processed {len(ranked_list)}/{len(places)}: {result['name']}")
            except Exception as e:
                print(f"  ❌ Error processing place {idx}: {e}")

    ranked_list.sort(key=lambda x: x['score'], reverse=True)

   
    console = Console()
    table_title = f"🏆 Top Rated '{dish.title()}' in {city.title()} 🏆"
    table = Table(title=table_title, show_header=True, header_style="bold cyan")

    table.add_column("Rank", style="dim", width=4)
    table.add_column("Name", width=30)
    table.add_column("Category")
    table.add_column("Avg Rating ⭐")
    table.add_column("Reviews 📝")
    table.add_column("Sentiment 😊")
    table.add_column("Final Score")
    table.add_column("Address")
    
    for i, item in enumerate(ranked_list):
        table.add_row(
            f"{i+1}", item['name'], item['category'], str(item['avg_rating']),
            str(item['reviews']), str(item['sentiment']), f"{item['score']:.2f}", item['address']
        )
    
    console.print(table)

    
    try:
        df = pd.DataFrame(ranked_list)
        clean_dish = dish.replace(" ", "_")
        clean_city = city.replace(" ", "_")
        csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\n Successfully saved detailed ranked results to '{csv_filename}'")
    except Exception as e:
        print(f"\n Error saving to CSV: {e}")