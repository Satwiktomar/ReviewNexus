
import logging

logger = logging.getLogger(__name__)

# Load model ONCE at startup (not per request) - saves 5-10 seconds!
print("Loading sentiment analysis model at startup...")
sentiment_pipeline = None
try:
    from transformers import pipeline
    import torch
    # Force CPU and disable gradients
    torch.set_grad_enabled(False)
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=-1,  # Use CPU
        batch_size=16  # Process multiple reviews at once
    )
    print("✅ Sentiment model loaded successfully (cached in memory)")
except Exception as e:
    print(f"⚠️ Warning: Could not load sentiment model: {e}")
    sentiment_pipeline = None

def get_sentiment_for_reviews(reviews: list):
    """
    Calculate sentiment score for a list of reviews using BATCH processing.
    
    Args:
        reviews: List of review dictionaries with 'text' key
        
    Returns:
        Sentiment score between -1 and 1
    """
    if not reviews or not sentiment_pipeline:
        return 0.0

    try:
        # Extract and prepare review texts (up to 10 reviews for speed)
        review_texts = [review.get('text', '')[:150] for review in reviews if review.get('text')][:10]
        
        if not review_texts:
            return 0.0
        
        # BATCH ANALYZE - process all at once (faster than one-by-one)
        sentiments = sentiment_pipeline(review_texts, truncation=True, batch_size=8)
        
        # Calculate aggregate sentiment score
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