
from transformers import pipeline


print("Loading sentiment analysis model...")
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("Model loaded.")

def get_sentiment_for_reviews(reviews: list):
   
    if not reviews:
        return 0

    
    sample_reviews = [review['text'] for review in reviews if review.get('text')][:10]
    
    if not sample_reviews:
        return 0
        
    sentiments = sentiment_pipeline(sample_reviews)
    
    score = 0
    for sentiment in sentiments:
       
        if sentiment['label'] == 'POSITIVE':
            score += sentiment['score']
        else:
            score -= sentiment['score']
            
    
    return score / len(sentiments)