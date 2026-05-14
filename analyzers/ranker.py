"""
Ranking engine — Bayesian composite score (0-10 scale).

Score breakdown:
  50% — Bayesian average rating  (dampens outliers with few reviews)
  30% — Sentiment score          (weighted by review-count confidence)
  20% — Popularity signal        (log-normalised review count)
"""

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

# ── Bayesian constants ────────────────────────────────────────
_PRIOR_MEAN  = 4.0   # global average rating across all restaurants
_MIN_VOTES   = 50    # reviews needed for "full trust"
_POP_CAP     = 5000  # review count capped at this for normalisation


def _generate_google_maps_url(name: str, address: str) -> str:
    query = f"{name} {address}".strip()
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"


def _validate_place_data(place: Dict) -> bool:
    if not isinstance(place, dict):
        return False
    name = place.get('name') or place.get('title')
    if not name or not isinstance(name, str) or not name.strip():
        return False
    return True


def _calculate_composite_score(
    avg_rating: float,
    review_count: int,
    sentiment_score: float,
) -> float:
    """
    Returns a composite score in [0, 10].

    1. Bayesian rating — pulls toward prior mean for low-review places
    2. Sentiment weight — scaled by review-count confidence (0→1 over 10 reviews)
    3. Popularity — log10-normalised, capped at POP_CAP reviews
    """
    # 1. Bayesian average
    bayesian = (
        (_PRIOR_MEAN * _MIN_VOTES + avg_rating * review_count)
        / (_MIN_VOTES + review_count)
    )

    # 2. Sentiment (confidence gated)
    conf     = min(review_count / 10.0, 1.0)
    weighted = sentiment_score * conf

    # 3. Popularity (log-normalised 0→1)
    capped_rc  = min(review_count, _POP_CAP)
    popularity = math.log10(capped_rc + 1) / math.log10(_POP_CAP + 1)

    composite = (
        0.50 * (bayesian / 5.0)
        + 0.30 * ((1.0 + weighted) / 2.0)
        + 0.20 * popularity
    ) * 10.0

    return round(max(0.0, min(10.0, composite)), 2)


def _process_place(place: Dict, city: str) -> Optional[Dict]:
    if not _validate_place_data(place):
        return None

    title        = (place.get('name') or place.get('title', 'N/A')).strip()
    avg_rating   = float(place.get('rating') or place.get('totalScore', 0))
    review_count = int(place.get('review_count') or place.get('reviewsCount', 0))
    category     = (place.get('category') or place.get('categoryName', 'Restaurant')).strip()
    address      = (place.get('address', city)).strip()
    reviews_list = place.get('reviews', [])
    latitude     = float(place.get('latitude', 0))
    longitude    = float(place.get('longitude', 0))

    if not isinstance(reviews_list, list):
        reviews_list = []

    sentiment_score = get_sentiment_for_reviews(reviews_list)

    final_score = _calculate_composite_score(avg_rating, review_count, sentiment_score)

    # Preserve the scraper URL if it looks like a real Maps link
    existing_url = place.get('url', '')
    url = (
        existing_url
        if existing_url and '/maps/' in existing_url
        else _generate_google_maps_url(title, address)
    )

    return {
        'name':       title,
        'category':   category,
        'avg_rating': round(avg_rating, 1),
        'reviews':    review_count,
        'sentiment':  f'{sentiment_score:.2f}',
        'score':      final_score,
        'address':    address,
        'url':        url,
        'latitude':   latitude,
        'longitude':  longitude,
    }


def analyze_and_rank(data_filename: str, dish: str, city: str) -> None:
    try:
        with open(data_filename, 'r', encoding='utf-8') as f:
            places = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f'Error loading {data_filename}: {e}')
        return

    if not places or not isinstance(places, list):
        print('No places to analyse.')
        return

    print(f'Analysing {len(places)} places for "{dish}" in "{city}"…')

    ranked_list: List[Dict] = []
    max_workers = min(4, len(places))

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_process_place, p, city): i for i, p in enumerate(places)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result()
                if result:
                    ranked_list.append(result)
                    print(f'  → {len(ranked_list)}/{len(places)}: {result["name"]} (score {result["score"]})')
            except Exception as e:
                print(f'  Error on place {idx}: {e}')

    if not ranked_list:
        print('No valid places after analysis.')
        return

    ranked_list.sort(key=lambda x: x['score'], reverse=True)

    # Console table
    console = Console()
    table = Table(
        title=f'Top "{dish.title()}" in {city.title()} — Bayesian Composite Scores',
        show_header=True, header_style='bold cyan',
    )
    table.add_column('#',          style='dim', width=3)
    table.add_column('Name',       width=28)
    table.add_column('Rating',     justify='center')
    table.add_column('Reviews',    justify='center')
    table.add_column('Sentiment',  justify='center')
    table.add_column('Score /10',  justify='center', style='bold green')

    for i, item in enumerate(ranked_list):
        table.add_row(
            str(i + 1),
            item['name'],
            str(item['avg_rating']),
            str(item['reviews']),
            str(item['sentiment']),
            str(item['score']),
        )
    console.print(table)

    # Save CSV
    try:
        df = pd.DataFrame(ranked_list)
        slug_dish = dish.replace(' ', '_').lower()
        slug_city = city.replace(' ', '_').lower()
        csv_path  = DATA_DIR / f'ranked_{slug_dish}_{slug_city}.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f'\nSaved → {csv_path}')
    except Exception as e:
        print(f'\nCSV save error: {e}')