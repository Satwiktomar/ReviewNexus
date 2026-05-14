"""
Lightweight sentiment analyzer using TextBlob.
Uses extremely low memory compared to Hugging Face Transformers,
allowing the app to run on platforms with 512MB RAM limits like Render.
"""

import logging
from typing import List, Dict
from textblob import TextBlob

logger = logging.getLogger(__name__)

def get_sentiment_for_reviews(reviews: List[Dict]) -> float:
    """
    Analyse a list of review dicts and return a sentiment score in [-1, +1].

    Each dict must have a 'text' key.
    Positive reviews contribute positively, negative ones negatively.
    Returns 0.0 if the reviews are empty.
    """
    if not reviews:
        return 0.0

    try:
        texts = [
            r.get('text', '')[:250]
            for r in reviews
            if r.get('text', '').strip()
        ][:10]  # sample at most 10 reviews

        if not texts:
            return 0.0

        total = 0.0
        for text in texts:
            # TextBlob polarity is a float within the range [-1.0, 1.0]
            analysis = TextBlob(text)
            total += analysis.sentiment.polarity

        return round(total / len(texts), 4)

    except Exception as exc:
        logger.error(f"Sentiment analysis error: {exc}")
        return 0.0