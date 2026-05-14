from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import re
import threading
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

try:
    from flask_cors import CORS
    _CORS_AVAILABLE = True
except ImportError:
    _CORS_AVAILABLE = False

from scrapers.google_maps_scraper import scrape_google_maps_reviews_sync
from analyzers.ranker import analyze_and_rank
from config.settings import (
    DATA_DIR, MAX_PLACES, MAX_REVIEWS_PER_PLACE,
    ENABLE_CACHE, CACHE_EXPIRY_HOURS, FLASK_DEBUG, SECRET_KEY,
)
from config.logger import setup_logging

logger = setup_logging('app')
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Allow Next.js dev server and production frontend to call the API
if _CORS_AVAILABLE:
    allowed_origins = ['http://localhost:3000', 'http://127.0.0.1:3000']
    frontend_url = os.environ.get('FRONTEND_URL')
    if frontend_url:
        allowed_origins.append(frontend_url)
    CORS(app, resources={r'/api/*': {'origins': allowed_origins}})

scraping_status = {}
status_lock = threading.Lock()

def sanitize_input(text: str) -> str:
    """Strip dangerous characters while preserving Unicode letters for city names."""
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()
    # Remove shell/HTML injection chars; keep Unicode letters, digits, spaces, hyphens
    text = re.sub(r'[<>"\'/\\;`|&$!]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text[:100]


_VALID_INPUT_RE = re.compile(r'^[\w\s\-\.]+$', re.UNICODE)


def validate_search_params(dish: str, city: str) -> tuple:
    dish = sanitize_input(dish)
    city = sanitize_input(city)

    if not dish or len(dish) < 2 or not _VALID_INPUT_RE.match(dish):
        raise ValueError("Invalid dish name — use letters, digits, spaces or hyphens")
    if not city or len(city) < 2 or not _VALID_INPUT_RE.match(city):
        raise ValueError("Invalid city name — use letters, digits, spaces or hyphens")

    return dish, city


def _cleanup_stale_status(max_entries: int = 200) -> None:
    """Prune the in-memory status dict to prevent unbounded growth."""
    with status_lock:
        if len(scraping_status) > max_entries:
            # Remove completed / error entries first
            stale = [
                k for k, v in scraping_status.items()
                if v.get('status') in ('completed', 'error')
            ]
            for k in stale:
                del scraping_status[k]

def is_cache_valid(filepath: Path) -> bool:
    if not ENABLE_CACHE or not filepath.exists():
        return False
    
    file_age = datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime)
    return file_age < timedelta(hours=CACHE_EXPIRY_HOURS)

def run_pipeline_in_background(dish: str, city: str, max_places: int = 15):
    status_key = f"{dish}_{city}"
    
    with status_lock:
        scraping_status[status_key] = {
            'status': 'scraping',
            'progress': 0,
            'message': 'Starting Google Maps scraper...'
        }
    
    logger.info(f"Starting pipeline for '{dish}' in '{city}'")
    
    try:
        clean_dish = dish.replace(" ", "_").lower()
        clean_city = city.replace(" ", "_").lower()
        
        if len(clean_dish) > 50 or len(clean_city) > 50:
            raise ValueError("Search terms too long")
        
        raw_data_filename = DATA_DIR / f"data_{clean_dish}_{clean_city}.json"
        ranked_csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'
        
        if raw_data_filename.exists() and is_cache_valid(raw_data_filename):
            logger.info(f"Using cached data: {raw_data_filename}")
            with status_lock:
                scraping_status[status_key]['progress'] = 50
                scraping_status[status_key]['message'] = 'Using cached data, starting analysis...'
        else:
            logger.info("Starting scraper...")
            with status_lock:
                scraping_status[status_key]['message'] = 'Scraping Google Maps...'

            def _progress_cb(pct: int, msg: str):
                with status_lock:
                    if status_key in scraping_status:
                        scraping_status[status_key]['progress'] = pct
                        scraping_status[status_key]['message']  = msg

            try:
                scraped_items = scrape_google_maps_reviews_sync(
                    search_terms=[f"best {dish} in {city}"],
                    location=city,
                    max_places=max_places,
                    max_reviews=MAX_REVIEWS_PER_PLACE,
                    progress_cb=_progress_cb,
                )
                
                if scraped_items:
                    with open(raw_data_filename, 'w', encoding='utf-8') as f:
                        json.dump(scraped_items, f, indent=4)
                    logger.info(f"Saved raw data to {raw_data_filename}")
                    with status_lock:
                        scraping_status[status_key]['progress'] = 50
                else:
                    logger.warning("Scraping returned no data")
                    with status_lock:
                        scraping_status[status_key]['status'] = 'error'
                        scraping_status[status_key]['message'] = 'No data found from scraper'
                    return
                    
            except Exception as e:
                logger.error(f"Scraping failed: {e}")
                with status_lock:
                    scraping_status[status_key]['status'] = 'error'
                    scraping_status[status_key]['message'] = f'Scraping error: {str(e)}'
                return
        
        with status_lock:
            scraping_status[status_key]['progress'] = 75
            scraping_status[status_key]['message'] = 'Analyzing and ranking...'
        
        logger.info("Starting analysis and ranking...")
        analyze_and_rank(
            data_filename=str(raw_data_filename),
            dish=dish,
            city=city
        )
        
        if ranked_csv_filename.exists():
            with status_lock:
                if status_key in scraping_status:
                    scraping_status[status_key]['status'] = 'completed'
                    scraping_status[status_key]['progress'] = 100
                    scraping_status[status_key]['message'] = 'Completed!'
            logger.info(f"Pipeline finished. Results saved to {ranked_csv_filename}")
        else:
            with status_lock:
                if status_key in scraping_status:
                    scraping_status[status_key]['status'] = 'error'
                    scraping_status[status_key]['message'] = 'Results file was not created'
            logger.error(f"Results file not found after analysis: {ranked_csv_filename}")
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        with status_lock:
            if status_key in scraping_status:
                scraping_status[status_key]['status'] = 'error'
                scraping_status[status_key]['message'] = f'Error: {str(e)}'

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dish = request.form.get('dish', '').strip()
        city = request.form.get('city', '').strip()
        max_places_str = request.form.get('max_places', '15').strip()
        
        try:
            dish, city = validate_search_params(dish, city)
            max_places = int(max_places_str)
            max_places = max(5, min(max_places, 20))
        except ValueError as e:
            return render_template('index.html', error=str(e)), 400
        
        logger.info(f"User search: {dish} in {city} (max {max_places} places)")
        
        status_key = f"{dish}_{city}"
        with status_lock:
            current_status = scraping_status.get(status_key, {})
        
        if current_status.get('status') in ['completed', 'error'] or status_key not in scraping_status:
            logger.info(f"Starting background pipeline for {dish} in {city}")
            thread = threading.Thread(
                target=run_pipeline_in_background,
                args=(dish, city, max_places),
                daemon=True
            )
            thread.start()
            return redirect(url_for('results', dish=dish, city=city))
        else:
            logger.info(f"Pipeline already running for {dish} in {city}. Redirecting to results.")
            return redirect(url_for('results', dish=dish, city=city))
    
    return render_template('index.html')

@app.route('/status/<string:dish>/<string:city>')
def get_status(dish: str, city: str):
    try:
        dish, city = validate_search_params(dish, city)
        status_key = f"{dish}_{city}"
        
        with status_lock:
            status = scraping_status.get(status_key, {'status': 'unknown', 'progress': 0})
        
        return jsonify(status)
    except ValueError:
        return jsonify({'status': 'error', 'progress': 0, 'message': 'Invalid parameters'}), 400

@app.route('/results/<string:dish>/<string:city>')
def results(dish: str, city: str):
    try:
        dish, city = validate_search_params(dish, city)
    except ValueError as e:
        return render_template('index.html', error=str(e)), 400
    
    clean_dish = dish.replace(" ", "_").lower()
    clean_city = city.replace(" ", "_").lower()
    ranked_csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'
    
    status_key = f"{dish}_{city}"
    
    if ranked_csv_filename.exists():
        logger.info(f"Results found for {dish} in {city}")
        try:
            df = pd.read_csv(ranked_csv_filename)
            places = df.to_dict(orient='records')
            # Ensure numeric columns are the right types
            for p in places:
                p['latitude']  = float(p.get('latitude',  0) or 0)
                p['longitude'] = float(p.get('longitude', 0) or 0)
                p['score']     = float(p.get('score', 0) or 0)
                p['avg_rating']= float(p.get('avg_rating', 0) or 0)
            return render_template('index.html', places=places, dish=dish, city=city, cached=True)
        except Exception as e:
            logger.error(f"Error reading results: {e}")
            return render_template('index.html', error='Error loading results'), 500
    
    with status_lock:
        current_status = scraping_status.get(status_key, {})
    
    if current_status.get('status') in ['scraping', 'analyzing']:
        logger.info(f"Pipeline already running for {dish} in {city}")
        return render_template('index.html', loading=True, dish=dish, city=city, status_key=status_key)
    
    logger.info(f"Starting background pipeline for {dish} in {city}")
    thread = threading.Thread(target=run_pipeline_in_background, args=(dish, city), daemon=True)
    thread.start()
    
    return render_template('index.html', loading=True, dish=dish, city=city, status_key=status_key)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


# ── JSON API for Next.js frontend ────────────────────────────

@app.route('/api/search', methods=['POST'])
def api_search():
    """Start a search pipeline. Returns immediately with status_key."""
    data = request.get_json(force=True, silent=True) or {}
    dish = data.get('dish', '').strip()
    city = data.get('city', '').strip()
    max_places_raw = data.get('max_places', 15)

    try:
        dish, city = validate_search_params(dish, city)
        max_places = max(5, min(int(max_places_raw), 20))
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400

    status_key = f'{dish}_{city}'
    with status_lock:
        current = scraping_status.get(status_key, {})

    if current.get('status') not in ('scraping', 'analyzing'):
        thread = threading.Thread(
            target=run_pipeline_in_background,
            args=(dish, city, max_places),
            daemon=True,
        )
        thread.start()

    return jsonify({'status_key': status_key, 'dish': dish, 'city': city})


@app.route('/api/status/<string:dish>/<string:city>')
def api_status(dish: str, city: str):
    """Progress polling endpoint for Next.js."""
    try:
        dish, city = validate_search_params(dish, city)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    status_key = f'{dish}_{city}'
    with status_lock:
        status = scraping_status.get(status_key, {'status': 'unknown', 'progress': 0})
    return jsonify(status)


@app.route('/api/results/<string:dish>/<string:city>')
def api_results(dish: str, city: str):
    """Return ranked restaurants as JSON for the Next.js frontend."""
    try:
        dish, city = validate_search_params(dish, city)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    clean_dish = dish.replace(' ', '_').lower()
    clean_city = city.replace(' ', '_').lower()
    csv_path   = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'

    if not csv_path.exists():
        return jsonify({'error': 'Results not ready yet'}), 404

    try:
        df = pd.read_csv(csv_path)
        places = df.to_dict(orient='records')
        for p in places:
            p['latitude']  = float(p.get('latitude',  0) or 0)
            p['longitude'] = float(p.get('longitude', 0) or 0)
            p['score']     = float(p.get('score',     0) or 0)
            p['avg_rating']= float(p.get('avg_rating',0) or 0)
            p['reviews']   = int(p.get('reviews',     0) or 0)

        # City centre coordinates (first valid place)
        city_lat = next((p['latitude']  for p in places if p['latitude']  != 0), 20.5937)
        city_lng = next((p['longitude'] for p in places if p['longitude'] != 0), 78.9629)

        return jsonify({
            'dish':        dish,
            'city':        city,
            'city_lat':    city_lat,
            'city_lng':    city_lng,
            'restaurants': places,
        })
    except Exception as e:
        logger.error(f'API results error: {e}')
        return jsonify({'error': 'Error reading results'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template('index.html', error='Internal server error'), 500 

if __name__ == '__main__':
    logger.info("Starting ReviewNexus application...")
    logger.info("Opening http://localhost:5000 in your browser...")
    app.run(debug=FLASK_DEBUG, use_reloader=False, port=5000, host='127.0.0.1')
