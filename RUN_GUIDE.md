## 🎯 COMPLETE STEP-BY-STEP GUIDE TO RUN FOODRANK

---

## ⚡ THE QUICK VERSION (Copy-Paste!)

```powershell
cd d:\foodrank
venv\Scripts\activate
pip install -r requirements.txt
playwright install
python app.py
```

Then open: **http://localhost:5000**

---

## 📋 DETAILED VERSION (With Explanations)

### **STEP 1️⃣: Open Terminal**

- Press: `Windows Key + R`
- Type: `powershell`
- Press: `Enter`

OR

- Right-click folder `d:\foodrank`
- Select "Open in Terminal"

---

### **STEP 2️⃣: Navigate to Project**

```powershell
cd d:\foodrank
```

You should see: `PS D:\foodrank>`

---

### **STEP 3️⃣: Activate Virtual Environment**

```powershell
venv\Scripts\activate
```

You should see: `(venv) PS D:\foodrank>`

✅ This means environment is active!

---

### **STEP 4️⃣: Install Dependencies (First Time Only)**

```powershell
pip install -r requirements.txt
```

**What happens:**
- Downloads Flask, pandas, playwright, transformers, torch, etc.
- Takes ~5-10 minutes
- Shows progress as it installs
- Ends with: "Successfully installed..."

---

### **STEP 5️⃣: Install Playwright Browsers (First Time Only)**

```powershell
playwright install
```

**What happens:**
- Downloads Chromium browser (~400MB)
- Takes ~2-3 minutes
- Shows installation progress
- Ends with: "Installation complete"

---

### **STEP 6️⃣: Run the Application**

```powershell
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * WARNING in werkzeug: This is a development server...
```

✅ **App is now running!**

---

### **STEP 7️⃣: Open Web Browser**

Open any browser and go to:
```
http://localhost:5000
```

You should see:
- FoodRank logo
- "Find the truly best food, ranked by data and AI"
- Search form with "What are you craving?" and "Which city?"

✅ **Website is live!**

---

### **STEP 8️⃣: Do Your First Search**

1. Enter dish: `Dosa`
2. Enter city: `Bengaluru`
3. Click: `🔍 Find Best Restaurants`

---

### **STEP 9️⃣: Watch Progress**

You'll see:
- Loading animation 🔄
- Progress bar (0% → 100%)
- Status messages:
  - "Scraping Google Maps reviews..."
  - "Analyzing and ranking..."
  - "Completed!"

**Time**: 2-5 minutes for first search

---

### **STEP 🔟: View Results**

You'll see:
- Table with ranked restaurants
- Columns: Rank, Restaurant, Rating, Reviews, Sentiment, Score
- Click restaurant name to open in Google Maps
- Results are saved for next time (instant!)

---

## 🔑 API Keys Needed?

### ❌ **NO API KEYS REQUIRED!**

| What | Needs API? | Why |
|------|-----------|-----|
| Google Maps Scraping | ❌ No | Uses Playwright |
| Sentiment Analysis | ❌ No | Uses open-source model |
| Web Server | ❌ No | Flask (local) |
| **Total Cost** | **FREE** | **$0** |

---

## ⚙️ Configuration (Optional)

If results are slow or you want to customize:

Edit `.env` file with any text editor:

```env
MAX_PLACES=15                    # Change to 10 for faster results
CACHE_EXPIRY_HOURS=24            # Change to 48 to cache longer
LOG_LEVEL=INFO                   # Change to DEBUG for more logs
HEADLESS_BROWSER=True            # Change to False to see browser
```

Save and restart: `python app.py`

---

## 📊 Expected First Run Flow

```
Start
  ↓
Open http://localhost:5000
  ↓
Search "Dosa in Bengaluru"
  ↓
[⏳ 2-5 minutes]
  ├─ Scraping Google Maps...
  ├─ Extracting reviews...
  ├─ Analyzing sentiment...
  └─ Ranking restaurants...
  ↓
Results page
  ├─ Restaurant 1: 9.5 score ⭐
  ├─ Restaurant 2: 9.2 score ⭐
  └─ Restaurant 3: 8.8 score ⭐
```

---

## 📁 File Locations After Running

### **View Generated Data:**
```powershell
# See what was scraped
Get-Content data/data_dosa_bengaluru.json

# See final rankings
Get-Content data/ranked_dosa_bengaluru.csv

# See application logs
Get-Content logs/app.log
```

---

## 🐛 If Something Goes Wrong

### **Error: "Playwright not installed"**
```powershell
playwright install
python app.py
```

### **Error: "Port 5000 in use"**
Another app is using port 5000. Either:
- Close other apps
- OR change port in app.py line: `app.run(port=5001)`

### **Error: "ModuleNotFoundError"**
```powershell
# Make sure environment is activated!
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### **Scraper returns no data**
- Check internet connection
- Try simpler search: "Pizza in Mumbai"
- Check logs: `Get-Content logs/app.log`

### **Very slow performance**
Edit `.env`:
```env
MAX_PLACES=5                 # Fewer restaurants
HEADLESS_BROWSER=True        # Should be True
```

---

## 🔄 For Subsequent Runs

After first time, just run:

```powershell
cd d:\foodrank
venv\Scripts\activate
python app.py
```

No need to reinstall anything!

---

## ⏹️ How to Stop the Server

In terminal, press: `Ctrl + C`

You'll see: `KeyboardInterrupt`

That's normal, server has stopped.

---

## 🎨 Using the App

### **First Search on a Dish/City**
- Takes 2-5 minutes
- Results saved automatically

### **Searching Same Dish/City Again**
- Instant! (uses cache)
- Valid for 24 hours

### **Searching Different Dish/City**
- Takes 2-5 minutes again
- Gets new data

---

## 🧪 Running Tests (Optional)

To verify everything works:

```powershell
python -m unittest tests.test_foodrank
```

You should see:
```
....................
------
Ran 20 tests in 0.123s
OK
```

✅ All tests passed!

---

## 📚 Other Files to Check

- `README.md` - Full documentation
- `QUICKSTART.md` - Quick reference
- `REFACTOR_SUMMARY.md` - What changed
- `app.py` - Main application code
- `config/settings.py` - Configuration
- `config/logger.py` - Logging setup

---

## 🚀 You're Ready!

**Summary:**
1. ✅ Open terminal
2. ✅ Navigate to `d:\foodrank`
3. ✅ Activate environment
4. ✅ Install dependencies
5. ✅ Install Playwright
6. ✅ Run `python app.py`
7. ✅ Open browser to `http://localhost:5000`
8. ✅ Search for restaurants
9. ✅ View results

**Total time**: ~20 minutes first time, 1 minute after

---

## 💡 Pro Tips

**Tip 1: Keep terminal open**
- Don't close terminal while app is running
- App runs in that terminal

**Tip 2: Multiple searches**
- Keep searching in browser
- Terminal will show logs

**Tip 3: View logs in real-time**
```powershell
tail -f logs/app.log
```

**Tip 4: Check what's cached**
```powershell
ls data/  # See what data exists
```

**Tip 5: Reset everything**
```powershell
rm data/*  # Clear cached data
rm logs/*  # Clear logs
# Now everything is fresh!
```

---

## ✅ Checklist Before Running

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated `(venv)`
- [ ] Dependencies installed `pip install -r requirements.txt`
- [ ] Playwright installed `playwright install`
- [ ] Terminal still open
- [ ] No other app on port 5000
- [ ] Good internet connection

---

## 🎯 Final Command

Everything in one go:

```powershell
cd d:\foodrank; venv\Scripts\activate; pip install -r requirements.txt; playwright install; python app.py
```

Then open: `http://localhost:5000`

---

## 🎉 DONE!

You now have a fully functional, free, AI-powered restaurant ranking system running locally!

**Enjoy discovering the best restaurants!** 🍜✨
