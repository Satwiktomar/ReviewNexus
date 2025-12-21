# FoodRank 🍜

**Find the truly best food, ranked by data and AI.**

FoodRank is a web application that scrapes restaurant reviews from Google Maps, analyzes them using AI-powered sentiment analysis, and ranks restaurants based on authentic customer feedback. It helps you discover the best places to eat any dish in any city.

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
