import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

print("Loading sentiment analysis model at startup...")
sentiment_pipeline = None
try:
    from transformers import pipeline
    import torch
    torch.set_grad_enabled(False)
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=-1,
        batch_size=16
    )
    print("Sentiment model loaded successfully")
except Exception as e:
    print(f"Warning: Could not load sentiment model: {e}")
    sentiment_pipeline = None

def get_sentiment_for_reviews(reviews: List[Dict]) -> float:
    if not reviews or not sentiment_pipeline:
        return 0.0

    try:
        review_texts = [review.get('text', '')[:150] for review in reviews if review.get('text')][:10]
        
        if not review_texts:
            return 0.0
        
        sentiments = sentiment_pipeline(review_texts, truncation=True, batch_size=8)
        
        total_score = 0
        for sentiment in sentiments:
            if sentiment['label'] == 'POSITIVE':
                total_score += sentiment['score']
            else:
                total_score -= sentiment['score']
        
        return total_score / len(sentiments)
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return 0.0