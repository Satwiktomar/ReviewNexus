
import logging

logger = logging.getLogger(__name__)

print("Loading sentiment analysis model...")
try:
    from transformers import pipeline
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=-1  # Use CPU to avoid GPU issues
    )
    print("Model loaded.")
except Exception as e:
    print(f"Warning: Could not load sentiment model: {e}")
    sentiment_pipeline = None

def get_sentiment_for_reviews(reviews: list):
    """
    Calculate sentiment score for a list of reviews.
    
    Args:
        reviews: List of review dictionaries with 'text' key
        
    Returns:
        Sentiment score between -1 and 1
    """
    if not reviews or not sentiment_pipeline:
        return 0.0

    try:
        # Sample reviews for faster processing
        sample_reviews = [review.get('text', '')[:200] for review in reviews if review.get('text')][:5]
        
        if not sample_reviews:
            return 0.0
        
        # Analyze sentiment
        sentiments = sentiment_pipeline(sample_reviews, truncation=True)
        
        score = 0
        for sentiment in sentiments:
            if sentiment['label'] == 'POSITIVE':
                score += sentiment['score']
            else:
                score -= sentiment['score']
        
        return score / len(sentiments)
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return 0.0