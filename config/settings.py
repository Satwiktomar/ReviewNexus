"""Configuration settings for FoodRank application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Flask configuration
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Scraper settings
MAX_PLACES = int(os.getenv('MAX_PLACES', '15'))
MAX_REVIEWS_PER_PLACE = int(os.getenv('MAX_REVIEWS_PER_PLACE', '20'))
SCRAPER_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', '60'))
HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'True').lower() == 'true'

# Analysis settings
SENTIMENT_MODEL = os.getenv('SENTIMENT_MODEL', 'distilbert-base-uncased-finetuned-sst-2-english')
SENTIMENT_SAMPLE_SIZE = int(os.getenv('SENTIMENT_SAMPLE_SIZE', '10'))

# Caching settings
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
CACHE_EXPIRY_HOURS = int(os.getenv('CACHE_EXPIRY_HOURS', '24'))

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API settings
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')  # Optional for future use
