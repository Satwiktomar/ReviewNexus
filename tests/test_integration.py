import unittest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.sentiment_analyzer import get_sentiment_for_reviews
from scrapers.google_maps_scraper import scrape_google_maps_reviews_sync
from analyzers.ranker import analyze_and_rank, _validate_place_data, _generate_google_maps_url

class TestSentimentAnalyzer(unittest.TestCase):
    
    def test_positive_reviews(self):
        reviews = [
            {'text': 'Excellent food and great service!'},
            {'text': 'Amazing experience, highly recommended!'}
        ]
        score = get_sentiment_for_reviews(reviews)
        self.assertGreater(score, 0)
    
    def test_negative_reviews(self):
        reviews = [
            {'text': 'Terrible food and bad service.'},
            {'text': 'Worst experience ever.'}
        ]
        score = get_sentiment_for_reviews(reviews)
        self.assertLess(score, 0)
    
    def test_empty_reviews(self):
        score = get_sentiment_for_reviews([])
        self.assertEqual(score, 0.0)
    
    def test_none_reviews(self):
        score = get_sentiment_for_reviews(None)
        self.assertEqual(score, 0.0)

class TestRanker(unittest.TestCase):
    
    def test_validate_place_data_valid(self):
        place = {'name': 'Test Restaurant', 'rating': 4.5}
        self.assertTrue(_validate_place_data(place))
    
    def test_validate_place_data_invalid_no_name(self):
        place = {'rating': 4.5}
        self.assertFalse(_validate_place_data(place))
    
    def test_validate_place_data_invalid_empty_name(self):
        place = {'name': '   ', 'rating': 4.5}
        self.assertFalse(_validate_place_data(place))
    
    def test_validate_place_data_invalid_not_dict(self):
        place = "not a dict"
        self.assertFalse(_validate_place_data(place))
    
    def test_generate_google_maps_url(self):
        url = _generate_google_maps_url("Test Restaurant", "Bengaluru")
        self.assertIn("google.com/maps/search", url)
        # urllib.parse.quote uses %20 for spaces (not +)
        self.assertTrue("Test%20Restaurant" in url or "Test+Restaurant" in url)
        self.assertIn("Bengaluru", url)


class TestScraper(unittest.TestCase):
    
    def test_scraper_returns_data(self):
        results = scrape_google_maps_reviews_sync(
            search_terms=["best pizza"],
            location="Mumbai",
            max_places=5,
            max_reviews=5
        )
        
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        for place in results:
            self.assertIn('name', place)
            self.assertIn('rating', place)
            self.assertIn('url', place)
            self.assertIsInstance(place['name'], str)
            self.assertTrue(len(place['name']) > 0)

if __name__ == '__main__':
    unittest.main()
