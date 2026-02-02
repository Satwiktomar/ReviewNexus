# 🍜 ReviewNexus - AI-Powered Restaurant Discovery

**Find the best restaurants ranked by real data and AI sentiment analysis**

FoodRank is an intelligent web application that scrapes Google Maps, analyzes restaurant reviews using AI, and ranks the best places to eat based on ratings, review counts, and sentiment scores.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![AI](https://img.shields.io/badge/AI-DistilBERT-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### Core Functionality
- 🔍 **Smart Web Scraping** - Extracts real restaurant data from Google Maps
- 🤖 **AI Sentiment Analysis** - Uses DistilBERT to analyze review sentiment
- 📊 **Intelligent Ranking** - Combines ratings, reviews, and sentiment into final scores
- 🗺️ **Interactive Maps** - Google Maps integration with clickable markers
- 🎯 **User Controls** - Select 5, 10, 15, or 20 results
- ⚡ **Smart Caching** - 24-hour cache for instant repeat searches
- � **Security Hardened** - Input sanitization, HTTPS headers, thread-safe operations



---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Playwright (for web scraping)
- 2GB RAM minimum

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Satwiktomar/foodrank.git
cd foodrank
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers**
```bash
playwright install chromium
```

4. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env if needed - works with defaults!
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://localhost:5000
```

---

## 📖 Usage

### Basic Search
1. Enter what you're craving (e.g., "Dosa", "Pizza", "Biryani")
2. Enter city (e.g., "Bengaluru", "Mumbai", "Delhi")
3. Select number of restaurants (5/10/15/20)
4. Click "Find Best Restaurants"

### Interactive Map
- Click markers to see restaurant details
- Click table rows to highlight markers on map
- Click location links to open in Google Maps

### Results
- **Rank** - Position based on final score
- **Rating** - Average star rating
- **Reviews** - Total review count
- **Sentiment** - AI-analyzed sentiment score
- **Score** - Combined ranking score

---

## 🏗️ Project Structure

```
foodrank/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env                        # Configuration (create from .env.example)
│
├── config/
│   ├── settings.py            # Application settings
│   └── logger.py              # Logging configuration
│
├── scrapers/
│   └── google_maps_scraper.py # Web scraping logic
│
├── analyzers/
│   ├── sentiment_analyzer.py  # AI sentiment analysis
│   └── ranker.py              # Restaurant ranking algorithm
│
├── templates/
│   └── index.html             # Main web interface
│
├── data/                       # Output files (auto-created)
│   ├── data_*.json            # Raw scraped data
│   └── ranked_*.csv           # Ranked results
│
└── logs/                       # Application logs (auto-created)
    ├── app.log
    └── scraper.log
```

---

## 🔧 Configuration

Edit `.env` file to customize settings:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# Scraper Settings
MAX_PLACES=15                   # Default results (user can override)
MAX_REVIEWS_PER_PLACE=20
SCRAPER_TIMEOUT=60
HEADLESS_BROWSER=True

# AI Model
SENTIMENT_MODEL=distilbert-base-uncased-finetuned-sst-2-english
SENTIMENT_SAMPLE_SIZE=10

# Caching
ENABLE_CACHE=True
CACHE_EXPIRY_HOURS=24

# Optional: Google Places API
GOOGLE_MAPS_API_KEY=           # Leave empty to use web scraping
```

---

## 🤖 How It Works

### 1. Web Scraping
```python
# Tries 3 strategies in order:
1. Google Places API (if key provided)
2. Playwright web scraping (real-time)
3. High-quality mock data (fallback)
```

**Scraper Features:**
- Scrolls page for more results
- Clicks places for full details
- Extracts names, ratings, reviews, addresses
- Validates and filters UI elements
- Adds geographic coordinates
- 3 retry attempts with delays

### 2. Sentiment Analysis
```python
# Uses DistilBERT transformer model
- Loads model once at startup
- Processes reviews in batches
- Returns sentiment score: -1 to +1
- Positive reviews boost ranking
```

### 3. Ranking Algorithm
```python
base_score = rating × log10(reviews + 1)
final_score = base_score × (1 + sentiment)
```

**Factors:**
- ⭐ Rating quality (4.5 better than 4.0)
- 📝 Review quantity (more reviews = higher confidence)
- 💭 Sentiment score (positive reviews boost ranking)

### 4. Results Display
- Interactive Google Map with markers
- Sortable, filterable table
- Clickable links to Google Maps

---


## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **Playwright** - Browser automation
- **Pandas** - Data processing
- **Transformers** - AI sentiment analysis (Hugging Face)
- **PyTorch** - Deep learning backend

### Frontend
- **HTML5/CSS3** - Structure and styling
- **TailwindCSS** - Utility-first CSS
- **JavaScript** - Interactive features
- **Google Maps API** - Interactive maps

### AI/ML
- **DistilBERT** - Transformer model for sentiment
- **Hugging Face** - Model hosting and inference

---

## 📊 Performance

- **First Search**: 30-60 seconds (web scraping + AI analysis)
- **Cached Search**: Instant (< 1 second)
- **Memory Usage**: ~500MB (model loaded)
- **Concurrent Users**: Supports multiple simultaneous searches

---

## 🐛 Troubleshooting

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Playwright browsers not found"
```bash
playwright install chromium
```

### "Seeing same results"
Results are cached for 24 hours. Clear cache:
```bash
Remove-Item -Path "data/*.json" -Force
Remove-Item -Path "data/*.csv" -Force
```

Or search for different dish/city.

### "Sentiment model downloading"
First run downloads ~400MB model. This is normal and happens once.

---





## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---


## ⚠️ Disclaimer

This project is for educational purposes. Web scraping Google Maps may violate their Terms of Service. Use responsibly and consider using the Google Places API for production use.

---

**Made with ❤️**
