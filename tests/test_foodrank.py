"""Unit tests for ReviewNexus application."""
import unittest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATA_DIR, MAX_PLACES
from config.logger import setup_logging


class TestConfiguration(unittest.TestCase):
    """Test configuration module."""
    
    def test_data_dir_exists(self):
        """Test that data directory exists."""
        self.assertTrue(DATA_DIR.exists())
    
    def test_max_places_is_positive(self):
        """Test that MAX_PLACES is positive."""
        self.assertGreater(MAX_PLACES, 0)


class TestLogger(unittest.TestCase):
    """Test logging setup."""
    
    def test_logger_initialization(self):
        """Test that logger initializes properly."""
        logger = setup_logging('test')
        self.assertIsNotNone(logger)
        self.assertTrue(hasattr(logger, 'info'))
        self.assertTrue(hasattr(logger, 'error'))


class TestDataHandling(unittest.TestCase):
    """Test data handling functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = {
            'places': [
                {
                    'name': 'Test Restaurant',
                    'rating': 4.5,
                    'reviews': [
                        {'text': 'Great food!'},
                        {'text': 'Excellent service'}
                    ]
                }
            ]
        }
    
    def test_json_serialization(self):
        """Test JSON serialization of data."""
        try:
            json_str = json.dumps(self.test_data)
            restored = json.loads(json_str)
            self.assertEqual(restored, self.test_data)
        except Exception as e:
            self.fail(f"JSON serialization failed: {e}")
    
    def test_data_structure(self):
        """Test data structure validation."""
        place = self.test_data['places'][0]
        self.assertIn('name', place)
        self.assertIn('rating', place)
        self.assertIn('reviews', place)


class TestScraperInterface(unittest.TestCase):
    """Test scraper interface."""
    
    def test_scraper_imports(self):
        """Test that scraper can be imported."""
        try:
            from scrapers.google_maps_scraper import scrape_google_maps_reviews_sync
            self.assertIsNotNone(scrape_google_maps_reviews_sync)
        except ImportError as e:
            self.fail(f"Failed to import scraper: {e}")
    
    def test_scraper_function_signature(self):
        """Test scraper function has correct signature."""
        from scrapers.google_maps_scraper import scrape_google_maps_reviews_sync
        import inspect
        
        sig = inspect.signature(scrape_google_maps_reviews_sync)
        params = list(sig.parameters.keys())
        
        self.assertIn('search_terms', params)
        self.assertIn('location', params)


class TestAnalyzerInterface(unittest.TestCase):
    """Test analyzer interface."""
    
    def test_analyzer_imports(self):
        """Test that analyzer can be imported."""
        try:
            from analyzers.ranker import analyze_and_rank
            self.assertIsNotNone(analyze_and_rank)
        except ImportError as e:
            self.fail(f"Failed to import analyzer: {e}")


class TestFlaskApp(unittest.TestCase):
    """Test Flask app routes."""
    
    def setUp(self):
        """Set up test client."""
        from app import app
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_index_route(self):
        """Test index route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_route(self):
        """Test health check route."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_404_handling(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
