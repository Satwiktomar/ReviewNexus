# FoodRank 🍜

**Find the truly best food, ranked by data and AI.**

FoodRank is a modern web application that scrapes restaurant reviews from Google Maps, analyzes them using AI-powered sentiment analysis, and ranks restaurants based on authentic customer feedback. It helps you discover the best places to eat any dish in any city—without paying expensive scraping fees.

## ✨ Key Improvements

- ✅ **Removed Apify Dependency** - Uses free Playwright for web scraping
- ✅ **Configuration Management** - Centralized `.env` file for all settings
- ✅ **Advanced Logging** - Rotating file logs and console output
- ✅ **Smart Caching** - Configurable cache expiry to reduce scraping
- ✅ **Progress Tracking** - Live progress updates with AJAX polling
- ✅ **Error Handling** - User-friendly error messages and proper exception handling
- ✅ **Unit Tests** - Comprehensive test suite
- ✅ **Enhanced UI** - Modern design with animations and progress bars

## Features

- 🔍 **Google Maps Integration** - Scrapes restaurant reviews and ratings without API costs
- 🤖 **AI Sentiment Analysis** - Uses DistilBERT for intelligent review analysis
- ⭐ **Smart Ranking** - Ranks restaurants by sentiment scores and customer feedback
- 🌐 **Web Interface** - Modern UI with Tailwind CSS and smooth animations
- ⚡ **Background Processing** - Non-blocking scraping and analysis
- 📊 **Data Export** - Results saved as CSV for further analysis
- 💾 **Smart Caching** - Configurable cache to save time on repeated searches
- 📈 **Progress Tracking** - Real-time updates during processing

## Project Structure

```
foodrank/
├── app.py                          # Main Flask application
├── requirements.txt                # Project dependencies (updated)
├── README.md                       # This file
├── run_analysis_only.py            # Script to run analysis without scraping
├── .env                            # Configuration file (updated)
├── .gitignore                      # Git ignore rules
│
├── config/                         # Configuration modules
│   ├── __init__.py
│   ├── settings.py                 # Configuration settings (NEW)
│   └── logger.py                   # Logging setup (NEW)
│
├── data/                           # Generated data files (git-ignored)
│   ├── data_*.json                 # Raw scraped data
│   └── ranked_*.csv                # Final rankings
│
├── logs/                           # Application logs (git-ignored)
│   └── *.log                       # Rotating log files
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   └── test_foodrank.py            # Test suite (NEW)
│
├── scrapers/                       # Web scraping modules
│   ├── __init__.py
│   └── google_maps_scraper.py      # Playwright-based scraper (UPDATED)
│
├── analyzers/                      # Analysis modules
│   ├── __init__.py
│   ├── ranker.py                   # Ranking logic
│   └── sentiment_analyzer.py       # AI sentiment analysis
│
└── templates/                      # HTML templates
    └── index.html                  # Web interface (UPDATED)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Satwiktomar/foodrank.git
   cd foodrank
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

5. **Configure environment (optional)**
   Edit `.env` file to customize settings:
   ```bash
   MAX_PLACES=15                    # Number of restaurants to scrape
   CACHE_EXPIRY_HOURS=24            # How long to cache results
   LOG_LEVEL=INFO                   # Logging verbosity
   ```

6. **Run the application**
   ```bash
   python app.py
   ```
   Then open `http://localhost:5000` in your browser

## Usage

### Web Interface

1. **Search**
   - Enter the dish name (e.g., "Dosa", "Pizza")
   - Enter the city (e.g., "Bengaluru", "Mumbai")
   - Click "Find Best Restaurants"

2. **Results**
   - View ranked restaurants with ratings and sentiment analysis
   - Click restaurant names to view on Google Maps
   - Results are cached for 24 hours by default

### Run Analysis Only

To analyze already-scraped data without scraping:

```bash
python run_analysis_only.py
```

Then enter:
- Dish name (matching filename)
- City name (matching filename)

## Configuration

Edit `.env` file to customize:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# Scraper
MAX_PLACES=15
MAX_REVIEWS_PER_PLACE=20
SCRAPER_TIMEOUT=60
HEADLESS_BROWSER=True

# Analysis
SENTIMENT_MODEL=distilbert-base-uncased-finetuned-sst-2-english
SENTIMENT_SAMPLE_SIZE=10

# Caching
ENABLE_CACHE=True
CACHE_EXPIRY_HOURS=24

# Logging
LOG_LEVEL=INFO
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.3 | Web framework |
| pandas | 2.0.3 | Data manipulation |
| playwright | 1.40.0 | Browser automation (no Apify!) |
| transformers | 4.30.2 | AI models for sentiment |
| torch | 2.0.1 | Deep learning backend |
| python-dotenv | 1.0.0 | Environment variables |
| requests | 2.31.0 | HTTP requests |
| rich | 13.5.2 | Terminal output formatting |

## How It Works

### 1. **Data Collection** (`scrapers/google_maps_scraper.py`)
   - Uses Playwright to automate browser (free alternative to Apify)
   - Navigates to Google Maps search results
   - Extracts place names, ratings, addresses, and reviews
   - Saves raw data as JSON

### 2. **Sentiment Analysis** (`analyzers/sentiment_analyzer.py`)
   - Analyzes sample reviews using DistilBERT
   - Calculates sentiment scores per restaurant
   - Generates composite sentiment metric

### 3. **Ranking** (`analyzers/ranker.py`)
   - Combines Google ratings with sentiment scores
   - Weighs both factors for final ranking
   - Exports results as ranked CSV

### 4. **Web Interface** (`templates/index.html`)
   - Modern search form
   - Live progress updates via AJAX
   - Results table with sorting
   - Error handling

## Output Format

### Results CSV Structure

```
place_name,rating,review_count,sentiment_score,address,score
"Pizza Palace",4.5,250,0.85,"123 Main St","9.2"
"Pasta Perfetto",4.3,180,0.78,"456 Oak Ave","8.8"
```

## Running Tests

```bash
python -m pytest tests/
# or
python -m unittest tests.test_foodrank
```

## Logging

Logs are saved to `logs/` directory with rotation:
- Console output (INFO level)
- File output with daily rotation
- Max file size: 10MB with 5 backups

View latest logs:
```bash
tail -f logs/app.log      # Flask app logs
tail -f logs/scraper.log  # Scraper logs
```

## API Endpoints

### Web Routes

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET, POST | Home page and search |
| `/results/<dish>/<city>` | GET | Display results |
| `/status/<dish>/<city>` | GET | Get scraping status (JSON) |
| `/health` | GET | Health check |

### Status Response

```json
{
  "status": "scraping",
  "progress": 50,
  "message": "Scraping Google Maps..."
}
```

## Advantages Over Apify

| Feature | FoodRank | Apify |
|---------|----------|-------|
| Cost | Free | $5-50+/month |
| Setup | Simple | Complex configuration |
| Learning curve | Low | Steep |
| Customization | Full control | Limited |
| Speed | Medium | Very fast |
| Reliability | Good | Excellent |

## Performance Tips

1. **Enable Caching** - First search takes 2-5 mins, subsequent are instant
2. **Reduce Max Places** - Set `MAX_PLACES=10` for faster results
3. **Use Headless Mode** - `HEADLESS_BROWSER=True` (default)
4. **Run on Faster Network** - Speeds up scraping significantly

## Troubleshooting

### "Playwright browsers not installed"
```bash
playwright install
```

### "Address already in use"
```bash
# Change port in app.py or use:
python app.py --port 5001
```

### "Scraping returns no data"
- Check your internet connection
- Ensure Google Maps is accessible
- Try with simpler search terms
- Check logs: `tail -f logs/scraper.log`

### "Sentiment analysis is slow"
- First run downloads the model (~400MB)
- Reduce `SENTIMENT_SAMPLE_SIZE` in `.env`
- Ensure you have enough RAM

## Future Enhancements

- [ ] Multi-language support
- [ ] Compare across multiple cities
- [ ] User ratings and comments
- [ ] Save favorite restaurants
- [ ] Export to PDF report
- [ ] API documentation
- [ ] Docker containerization
- [ ] Database integration
- [ ] Mobile app
- [ ] Advanced filtering and sorting

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available for educational purposes.

## Author

Created by [Satwik Tomar](https://github.com/Satwiktomar)

## Disclaimer

This tool is for educational purposes. Respect Google Maps' terms of service. The project automatically implements courteous delays and respectful scraping practices.

## Features

- 🔍 **Google Maps Integration** - Scrapes real restaurant reviews and ratings
- 🤖 **AI Sentiment Analysis** - Uses DistilBERT for intelligent review analysis
- ⭐ **Smart Ranking** - Ranks restaurants based on sentiment scores and customer reviews
- 🌐 **Web Interface** - Clean, modern UI built with Flask and Tailwind CSS
- ⚡ **Background Processing** - Asynchronous data collection and analysis
- 📊 **Data Export** - Results saved as CSV for further analysis

## Project Structure

```
foodrank/
├── app.py                          # Main Flask application
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
├── run_analysis_only.py            # Script to run analysis without scraping
│
├── config/                         # Configuration files
│   └── __init__.py
│
├── data/                           # Generated data files (git-ignored)
│   ├── data_*.json                # Raw scraped data
│   └── ranked_*.csv               # Final rankings
│
├── logs/                           # Application logs (git-ignored)
│   └── *.log
│
├── tests/                          # Unit tests
│   └── __init__.py
│
├── scrapers/                       # Web scraping modules
│   ├── __init__.py
│   ├── google_maps_scraper.py      # Google Maps scraper
│   └── __pycache__/
│
├── analyzers/                      # Analysis modules
│   ├── __init__.py
│   ├── ranker.py                   # Ranking logic
│   ├── sentiment_analyzer.py       # AI sentiment analysis
│   └── __pycache__/
│
└── templates/                      # HTML templates
    └── index.html                  # Web interface
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Apify API token (for Google Maps scraping)

### Setup

1. **Clone or download the project**
   ```bash
   cd foodrank
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Apify token**
   - Get an API token from [Apify](https://apify.com/)
   - Update `APIFY_TOKEN` in `app.py` with your token

## Usage

### Run the Web Application

```bash
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

**Steps:**
1. Enter the dish name (e.g., "Dosa", "Pizza", "Biryani")
2. Enter the city (e.g., "Bengaluru", "Mumbai")
3. Click "Search"
4. The app will scrape reviews and analyze them in the background
5. Results will display once processing is complete

### Run Analysis Only

If you already have scraped data and want to re-analyze it:

```bash
python run_analysis_only.py
```

## How It Works

### 1. **Data Collection** (`scrapers/google_maps_scraper.py`)
   - Uses Apify's Google Maps crawler to find restaurants
   - Collects place names, ratings, and customer reviews
   - Saves raw data as JSON

### 2. **Sentiment Analysis** (`analyzers/sentiment_analyzer.py`)
   - Uses DistilBERT model for sentiment classification
   - Analyzes sample reviews from each restaurant
   - Generates sentiment scores (0-1 scale)

### 3. **Ranking** (`analyzers/ranker.py`)
   - Combines sentiment scores with Google ratings
   - Ranks restaurants by quality
   - Outputs ranked results as CSV

### 4. **Web Interface** (`templates/index.html`)
   - Search form for dish and city
   - Loading page while data is processed
   - Results table with restaurant details

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.3 | Web framework |
| pandas | 2.0.3 | Data manipulation |
| apify-client | 1.5.2 | Google Maps scraping |
| transformers | 4.30.2 | AI sentiment analysis |
| torch | 2.0.1 | Deep learning backend |
| rich | 13.5.2 | Terminal formatting |

## Configuration

**In `app.py`:**
```python
APIFY_TOKEN = "your_token_here"   # Your Apify API token
MAX_RESULTS = 15                   # Number of restaurants to scrape
```

## Output

Results are saved in two formats:

- **Raw Data**: `data_{dish}_{city}.json` - Complete scraped data
- **Ranked Results**: `ranked_{dish}_{city}.csv` - Final rankings with columns:
  - `place_name` - Restaurant name
  - `rating` - Google Maps rating
  - `review_count` - Number of reviews
  - `sentiment_score` - AI-calculated sentiment (0-1)
  - `address` - Restaurant location
  - `type` - Cuisine type

## Notes

- The first search for a dish-city combination may take 2-5 minutes to complete
- Subsequent searches use cached results for faster loading
- The app uses background threading to avoid blocking the web interface
- Sentiment analysis samples up to 10 reviews per restaurant for efficiency

## Future Enhancements

- [ ] Cached results management and refresh options
- [ ] Multiple city/country support
- [ ] User reviews and ratings
- [ ] Export results to PDF
- [ ] Advanced filtering and sorting

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please check:
1. Apify API token is valid and has sufficient credits
2. Internet connection is stable
3. Required Python packages are installed
