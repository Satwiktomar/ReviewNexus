import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Flask
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Scraper
MAX_PLACES = max(1, min(int(os.getenv('MAX_PLACES', '15')), 50))
MAX_REVIEWS_PER_PLACE = max(1, min(int(os.getenv('MAX_REVIEWS_PER_PLACE', '20')), 100))
SCRAPER_TIMEOUT = max(10, min(int(os.getenv('SCRAPER_TIMEOUT', '60')), 300))
HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'True').lower() == 'true'
SCRAPER_MAX_RETRIES = 3
SCRAPER_RETRY_DELAY = 2

# Sentiment model (DistilBERT — lazy-loaded on first use)
SENTIMENT_MODEL = os.getenv(
    'SENTIMENT_MODEL',
    'distilbert-base-uncased-finetuned-sst-2-english',
)
SENTIMENT_SAMPLE_SIZE = max(1, min(int(os.getenv('SENTIMENT_SAMPLE_SIZE', '10')), 50))

# Geocoding via Nominatim (OpenStreetMap — no API key required)
NOMINATIM_USER_AGENT = os.getenv('NOMINATIM_USER_AGENT', 'ReviewNexus/1.0 (educational project)')

# Caching
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
CACHE_EXPIRY_HOURS = max(1, min(int(os.getenv('CACHE_EXPIRY_HOURS', '24')), 168))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# File handling
ALLOWED_EXTENSIONS = {'.json', '.csv'}
MAX_FILENAME_LENGTH = 200
