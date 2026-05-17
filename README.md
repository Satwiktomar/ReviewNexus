# 🌐 ReviewNexus

**A Global AI-Powered Restaurant Discovery Engine**

ReviewNexus is a production-grade, globally accessible web application that scrapes real-time data from Google Maps, performs natural language processing (NLP) on restaurant reviews, and ranks places using a robust Bayesian composite formula.

![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black)
![Flask](https://img.shields.io/badge/Backend-Flask-green)
![Playwright](https://img.shields.io/badge/Scraper-Playwright-orange)
![Deploy](https://img.shields.io/badge/Deployment-Vercel%20%26%20Render-blue)

**🚀 [Try the Live Demo on Vercel](https://reviewnexus.vercel.app)**


---

## ✨ Features

- 🌍 **Global Support**: Search for restaurants in any city worldwide. Powered by OpenStreetMap's Nominatim geocoding.
- 🤖 **AI Sentiment Analysis**: Analyzes the text of real reviews using `TextBlob` (lexicon-based NLP) to evaluate customer sentiment dynamically.
- 📐 **Bayesian Ranking Engine**: Calculates a true score based on a proprietary weight formula:
  - 45% Normalized Rating
  - 30% Normalized Review Volume
  - 25% AI Sentiment Score
- 🎭 **Headless Scraping**: Automatically navigates Google Maps using Playwright, bypassing the need for expensive API keys. 
- 🌐 **Cinematic 3D UI**: Features a fully interactive 3D globe built with `react-globe.gl` representing search results spatially, complete with dynamic day/night cycles.

---

## 🏗️ System Architecture

ReviewNexus uses a decoupled architecture for maximum scalability and deployment flexibility.

### Frontend (Next.js 15)
- **Framework**: React 19 / Next.js 15 App Router
- **Styling**: Tailwind CSS v4, Lucide React icons
- **3D Engine**: `react-globe.gl` + Three.js
- **Deployment**: Hosted on **Vercel**

### Backend (Python / Flask)
- **Framework**: Flask + Gunicorn (1 worker, 4 threads for memory optimization)
- **Scraper**: Playwright (Chromium) - optimized to block heavy assets (images/CSS) to save RAM.
- **AI/NLP**: `TextBlob` (replaces DistilBERT to fit seamlessly within 512MB RAM limits)
- **Deployment**: Containerized via Docker and hosted on **Render** (Free Tier).

---

## 🚀 Local Development

### 1. Backend Setup (Python)
```bash
# Clone the repository
git clone https://github.com/Satwiktomar/ReviewNexus.git
cd ReviewNexus

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium --with-deps

# Run the Flask API
python app.py
```
*The backend will run on `http://localhost:5000`.*

### 2. Frontend Setup (Next.js)
```bash
# Open a new terminal and navigate to the frontend
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```
*The frontend will run on `http://localhost:3000`.*

---

## 🌐 Production Deployment

ReviewNexus is fully configured for cloud deployment.

**Backend (Render)**
- Connect your GitHub repo to Render as a Web Service.
- Set the Build Command: `pip install -r requirements.txt && playwright install chromium --with-deps`
- Set the Start Command: `gunicorn app:app -w 1 --threads 4 --bind 0.0.0.0:$PORT`
- *Environment Variables*: Set `FRONTEND_URL` to your Vercel domain to secure CORS.

**Frontend (Vercel)**
- Connect the `frontend` directory to Vercel.
- *Environment Variables*: Set `NEXT_PUBLIC_FLASK_URL` to your Render backend URL (e.g., `https://reviewnexus-api.onrender.com`).

---

## 📊 The Ranking Algorithm

The engine normalizes raw scraped metrics into a 0-1 scale to compute a final, unbiased score:

```text
Final Score = (0.45 * Normalized Rating) + (0.30 * Normalized Volume) + (0.25 * Sentiment Score)
```
- **Normalized Rating**: `(Rating - 1.0) / 4.0`
- **Normalized Volume**: `min(ReviewCount / 1000, 1.0)`
- **Sentiment Score**: Calculated via TextBlob polarity `[-1.0, 1.0]`, normalized to `[0.0, 1.0]`.

---

## ⚠️ Disclaimer
This project is for educational and portfolio purposes. Headless web scraping of Google Maps may violate Google's Terms of Service if done at scale. Use responsibly.
