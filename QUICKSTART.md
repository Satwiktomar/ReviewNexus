## FoodRank - Complete Setup & Run Guide 🚀

### ✅ Prerequisites Check

You have:
- ✅ Python 3.11.9 installed (perfect!)
- ✅ Project files in `D:\foodrank`
- ✅ Virtual environment ready (venv folder)
- ✅ Git configured and connected to GitHub

### 🔑 API Keys Required?

**Great news: NO API KEYS NEEDED!** 🎉

| Component | API Key? | Notes |
|-----------|----------|-------|
| Google Maps Scraping | ❌ No | Uses Playwright (free) |
| Sentiment Analysis | ❌ No | DistilBERT (open source) |
| Flask Web Server | ❌ No | Local only |
| **Total Cost** | **$0** | **Completely Free!** |

### 📋 Step-by-Step Setup

#### **Step 1: Activate Virtual Environment**

```powershell
cd d:\foodrank
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

---

#### **Step 2: Install Dependencies**

```powershell
pip install -r requirements.txt
```

This will install:
- Flask (web server)
- Pandas (data handling)
- Playwright (browser automation - NO APIFY!)
- Transformers (sentiment analysis)
- Torch (AI model)
- Python-dotenv (environment config)
- And more...

**Time**: ~5-10 minutes on first install

---

#### **Step 3: Install Playwright Browsers**

```powershell
playwright install
```

This downloads the Chromium browser (~400MB).

**Time**: ~2-3 minutes

---

#### **Step 4: Verify Configuration**

Check `.env` file (all defaults are good):

```powershell
cat .env
```

Should show:
```
FLASK_ENV=development
FLASK_DEBUG=True
MAX_PLACES=15
ENABLE_CACHE=True
CACHE_EXPIRY_HOURS=24
LOG_LEVEL=INFO
```

✅ **No changes needed!** All settings are optimized.

---

#### **Step 5: Run the Application**

```powershell
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 WARNING in werkzeug: This is a development server...
```

---

#### **Step 6: Access the Web Interface**

Open your browser and go to:
```
http://localhost:5000
```

You should see the **FoodRank** homepage with search form.

---

### 🎯 First Search - What to Expect

1. **Enter search:**
   - Dish: `Dosa`
   - City: `Bengaluru`

2. **Click "Find Best Restaurants"**

3. **First search takes 2-5 minutes** ⏳
   - Scraping Google Maps
   - Extracting reviews
   - Analyzing sentiment
   - Ranking restaurants

4. **You'll see:**
   - Live progress bar (0-100%)
   - Status messages
   - Auto-refresh when complete

5. **Results page shows:**
   - Ranked list of restaurants
   - Ratings and review counts
   - Sentiment analysis scores
   - Final ranking score

---

### ⚡ Quick Reference: All Commands

```powershell
# Activate environment
cd d:\foodrank
venv\Scripts\activate

# Install packages (first time only)
pip install -r requirements.txt

# Install Playwright browsers (first time only)
playwright install

# Run the web app
python app.py

# Run analysis only (if you have data files)
python run_analysis_only.py

# Run tests
python -m unittest tests.test_foodrank

# Deactivate environment
deactivate
```

---

### 📊 Configuration Options

You can customize in `.env` file:

```env
# Faster results (less data)
MAX_PLACES=10                # Default: 15
SENTIMENT_SAMPLE_SIZE=5      # Default: 10

# Slower but more thorough
MAX_PLACES=30                # More restaurants
CACHE_EXPIRY_HOURS=48        # Cache longer

# Development
LOG_LEVEL=DEBUG              # More verbose logging
HEADLESS_BROWSER=False       # See browser (slow!)
```

Then restart: `python app.py`

---

### 🗂️ File Locations

After running, check:

```powershell
# View logs
Get-Content logs/app.log

# View generated data
Get-ChildItem data/

# View scraped data
Get-Content data/data_dosa_bengaluru.json

# View final rankings
Get-Content data/ranked_dosa_bengaluru.csv
```

---

### ✨ Features After First Run

1. **Cached Results** 💾
   - Same search = instant results
   - Valid for 24 hours
   - Clear by deleting files in `data/` folder

2. **Logs** 📝
   - Check `logs/app.log` for debugging
   - Auto-rotates (max 10MB per file)

3. **Export** 📊
   - Results saved as CSV
   - Can open in Excel, Python, etc.

---

### 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Playwright not installed"** | Run: `playwright install` |
| **"Address already in use"** | Change port in app.py or close other app |
| **"No data from scraper"** | Check internet, try simpler search terms |
| **"Slow performance"** | Reduce `MAX_PLACES`, use `HEADLESS_BROWSER=True` |
| **"ModuleNotFoundError"** | Activate venv: `venv\Scripts\activate` |
| **"Port 5000 in use"** | Set different port in app.py (app.run(port=5001)) |

---

### 🎮 Testing Without Real Scraping

To test with existing data:

```powershell
python run_analysis_only.py

# Enter when prompted:
# Dish: dosa
# City: bengaluru

# It will use: data/data_dosa_bengaluru.json
```

---

### 📈 Next Steps

1. ✅ Run first search
2. ✅ Check results quality
3. ✅ Try different dishes/cities
4. ✅ Export results as CSV
5. ✅ Commit to GitHub
6. ✅ Customize as needed

---

### 💡 Tips & Tricks

**Speed up results:**
```env
MAX_PLACES=5
MAX_REVIEWS_PER_PLACE=10
```

**See browser scraping:**
```env
HEADLESS_BROWSER=False
```

**More detailed logs:**
```env
LOG_LEVEL=DEBUG
```

**Never expire cache:**
```env
CACHE_EXPIRY_HOURS=999999
```

---

### ✅ You're Ready!

```powershell
cd d:\foodrank
venv\Scripts\activate
python app.py
# Then open: http://localhost:5000
```

**Enjoy discovering the best restaurants!** 🍜✨
