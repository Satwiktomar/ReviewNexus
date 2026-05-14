"""
Lazy-loading sentiment analyzer using DistilBERT.
Model is loaded on first use (not at import time) via a thread-safe singleton,
so the Flask server starts in < 2 seconds instead of blocking for minutes.
"""

import threading
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

_pipeline = None
_pipeline_lock = threading.Lock()
_load_failed = False  # If model loading fails once, skip retrying every call


def _get_pipeline():
    """Return the (lazily loaded) sentiment pipeline, or None if unavailable."""
    global _pipeline, _load_failed

    if _pipeline is not None:
        return _pipeline
    if _load_failed:
        return None

    with _pipeline_lock:
        # Double-checked locking
        if _pipeline is not None:
            return _pipeline
        if _load_failed:
            return None

        logger.info("Loading DistilBERT sentiment model (first use)…")
        try:
            from transformers import pipeline
            import torch

            torch.set_grad_enabled(False)
            _pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1,       # CPU
                batch_size=16,
            )
            logger.info("Sentiment model loaded successfully")
        except Exception as exc:
            logger.warning(f"Could not load sentiment model: {exc} — scores will default to 0.0")
            _load_failed = True

    return _pipeline


def get_sentiment_for_reviews(reviews: List[Dict]) -> float:
    """
    Analyse a list of review dicts and return a sentiment score in [-1, +1].

    Each dict must have a 'text' key.
    Positive reviews contribute positively, negative ones negatively.
    Returns 0.0 if the model is unavailable or reviews are empty.
    """
    if not reviews:
        return 0.0

    pipe = _get_pipeline()
    if pipe is None:
        return 0.0

    try:
        texts = [
            r.get('text', '')[:150]
            for r in reviews
            if r.get('text', '').strip()
        ][:10]  # sample at most 10 reviews

        if not texts:
            return 0.0

        sentiments = pipe(texts, truncation=True, batch_size=8)

        total = 0.0
        for s in sentiments:
            score = s['score']
            total += score if s['label'] == 'POSITIVE' else -score

        return round(total / len(sentiments), 4)

    except Exception as exc:
        logger.error(f"Sentiment analysis error: {exc}")
        return 0.0