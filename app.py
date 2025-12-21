from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

from scrapers.google_maps_scraper import scrape_google_maps_reviews_sync
from analyzers.ranker import analyze_and_rank
from config.settings import DATA_DIR, MAX_PLACES, MAX_REVIEWS_PER_PLACE, ENABLE_CACHE, CACHE_EXPIRY_HOURS, FLASK_DEBUG
from config.logger import setup_logging

logger = setup_logging('app')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'foodrank-secret-key'

# Global dict to track scraping progress
scraping_status = {}

def is_cache_valid(filepath: Path) -> bool:
    """Check if cached data is still valid."""
    if not ENABLE_CACHE or not filepath.exists():
        return False
    
    file_age = datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime)
    return file_age < timedelta(hours=CACHE_EXPIRY_HOURS)


def run_pipeline_in_background(dish: str, city: str):
    """Run scraping and analysis in background thread."""
    status_key = f"{dish}_{city}"
    scraping_status[status_key] = {
        'status': 'scraping',
        'progress': 0,
        'message': 'Starting Google Maps scraper...'
    }
    
    logger.info(f"BACKGROUND THREAD: Starting pipeline for '{dish}' in '{city}'")
    
    try:
        clean_dish = dish.replace(" ", "_").lower()
        clean_city = city.replace(" ", "_").lower()
        raw_data_filename = DATA_DIR / f"data_{clean_dish}_{clean_city}.json"
        ranked_csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'
        
        
        if raw_data_filename.exists() and is_cache_valid(raw_data_filename):
            logger.info(f"Using cached data: {raw_data_filename}")
            scraping_status[status_key]['progress'] = 50
            scraping_status[status_key]['message'] = 'Using cached data, starting analysis...'
        else:
           
            logger.info("Raw data not found or expired. Starting Apify scraper...")
            scraping_status[status_key]['message'] = 'Scraping Google Maps...'
            
            try:
                scraped_items = scrape_google_maps_reviews_sync(
                    search_terms=[f"best {dish} in {city}"],
                    location=f"{city}, India",
                    max_places=MAX_PLACES,
                    max_reviews=MAX_REVIEWS_PER_PLACE
                )
                
                if scraped_items:
                    with open(raw_data_filename, 'w', encoding='utf-8') as f:
                        json.dump(scraped_items, f, indent=4)
                    logger.info(f"Saved raw data to {raw_data_filename}")
                    scraping_status[status_key]['progress'] = 50
                else:
                    logger.warning("Scraping returned no data")
                    scraping_status[status_key]['status'] = 'error'
                    scraping_status[status_key]['message'] = 'No data found from scraper'
                    return
                    
            except Exception as e:
                logger.error(f"Scraping failed: {e}")
                scraping_status[status_key]['status'] = 'error'
                scraping_status[status_key]['message'] = f'Scraping error: {str(e)}'
                return
        
        # Analyze and rank
        scraping_status[status_key]['progress'] = 75
        scraping_status[status_key]['message'] = 'Analyzing and ranking...'
        
        logger.info("Starting analysis and ranking...")
        analyze_and_rank(
            data_filename=str(raw_data_filename),
            dish=dish,
            city=city
        )
        
        scraping_status[status_key]['status'] = 'completed'
        scraping_status[status_key]['progress'] = 100
        scraping_status[status_key]['message'] = 'Completed!'
        logger.info(f"Pipeline finished. Results saved to {ranked_csv_filename}")
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        scraping_status[status_key]['status'] = 'error'
        scraping_status[status_key]['message'] = f'Error: {str(e)}'

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle both form display and search processing."""
    if request.method == 'POST':
        dish = request.form.get('dish', '').strip() or 'dosa'
        city = request.form.get('city', '').strip() or 'Bengaluru'
        
        if not dish or not city:
            return render_template('index.html', error='Please enter both dish and city'), 400
        
        logger.info(f"User search: {dish} in {city}")
        return redirect(f'/results/{dish}/{city}')
    
    return render_template('index.html')


@app.route('/status/<string:dish>/<string:city>')
def get_status(dish: str, city: str):
    """Get scraping status for AJAX updates."""
    status_key = f"{dish}_{city}"
    return jsonify(scraping_status.get(status_key, {'status': 'unknown', 'progress': 0}))


@app.route('/results/<string:dish>/<string:city>')
def results(dish: str, city: str):
    """Display results or loading page."""
    clean_dish = dish.replace(" ", "_").lower()
    clean_city = city.replace(" ", "_").lower()
    ranked_csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'
    
    status_key = f"{dish}_{city}"
    
    # First check if results file exists
    if ranked_csv_filename.exists():
        logger.info(f"Results found for {dish} in {city}")
        # Clear status to prevent re-triggering
        if status_key in scraping_status:
            del scraping_status[status_key]
        try:
            df = pd.read_csv(ranked_csv_filename)
            places = df.to_dict(orient='records')
            return render_template('index.html', places=places, dish=dish, city=city, cached=True)
        except Exception as e:
            logger.error(f"Error reading results: {e}")
            return render_template('index.html', error='Error loading results'), 500
    
    # Check if currently processing
    current_status = scraping_status.get(status_key, {})
    if current_status.get('status') in ['scraping', 'analyzing']:
        # Already processing, just return loading page
        logger.info(f"Pipeline already running for {dish} in {city}")
        return render_template('index.html', loading=True, dish=dish, city=city, status_key=status_key)
    
    # Start new pipeline only if not already running
    logger.info(f"Starting background pipeline for {dish} in {city}")
    thread = threading.Thread(target=run_pipeline_in_background, args=(dish, city), daemon=True)
    thread.start()
    
    return render_template('index.html', loading=True, dish=dish, city=city, status_key=status_key)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('index.html', error='Internal server error'), 500 


if __name__ == '__main__':
    logger.info("Starting FoodRank application...")
    logger.info("Opening http://localhost:5000 in your browser...")
    app.run(debug=FLASK_DEBUG, use_reloader=False, port=5000)
