from flask import Flask, render_template, request, redirect, url_for
import os
import json
import threading
import pandas as pd
from pathlib import Path

from scrapers.google_maps_scraper import scrape_google_maps_reviews
from analyzers.ranker import analyze_and_rank

# Set up data directory
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


APIFY_TOKEN = apifytkn  
MAX_RESULTS = 15

def run_pipeline_in_background(dish, city):
   
    print(f"BACKGROUND THREAD: Starting pipeline for '{dish}' in '{city}'")

    
    clean_dish = dish.replace(" ", "_").lower()
    clean_city = city.replace(" ", "_").lower()
    raw_data_filename = DATA_DIR / f"data_{clean_dish}_{clean_city}.json"
    ranked_csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'

    
    if not raw_data_filename.exists():
        print(f"BACKGROUND THREAD: Raw data not found. Starting Apify scraper...")
        scraped_items = scrape_google_maps_reviews(
            api_token=APIFY_TOKEN,
            search_terms=[f"best {dish} in {city}"],
            location=f"{city}, India",
            max_places=MAX_RESULTS
        )
        if scraped_items:
            with open(raw_data_filename, 'w', encoding='utf-8') as f:
                json.dump(scraped_items, f, indent=4)
            print(f"BACKGROUND THREAD: Saved raw data to {raw_data_filename}")
        else:
            print("BACKGROUND THREAD: Scraping failed or returned no data.")
            return 
    else:
        print(f"BACKGROUND THREAD: Found existing raw data at {raw_data_filename}.")

   
    print("BACKGROUND THREAD: Starting analysis and ranking...")
    analyze_and_rank(
        data_filename=raw_data_filename,
        dish=dish,
        city=city
    )
    print(f"BACKGROUND THREAD: Pipeline finished. Results saved to {ranked_csv_filename}.")

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles both the initial form display and processing user searches.
    """
    if request.method == 'POST':
        dish = request.form.get('dish') or 'dosa'
        city = request.form.get('city') or 'Bengaluru'
        
        
        return redirect(url_for('results', dish=dish, city=city))
        
    
    return render_template('index.html')

@app.route('/results/<string:dish>/<string:city>')
def results(dish, city):
    """
    Displays results if they exist, or a loading page if they are being generated.
    """
    clean_dish = dish.replace(" ", "_").lower()
    clean_city = city.replace(" ", "_").lower()
    ranked_csv_filename = DATA_DIR / f'ranked_{clean_dish}_{clean_city}.csv'

    
    if ranked_csv_filename.exists():
       
        print(f"Results file found at {ranked_csv_filename}. Displaying data.")
        df = pd.read_csv(ranked_csv_filename)
       
        places = df.to_dict(orient='records')
        return render_template('index.html', places=places, dish=dish, city=city)
    else:
       
        print(f"Results file not found. Starting background pipeline for '{dish}' in '{city}'.")
        thread = threading.Thread(target=run_pipeline_in_background, args=(dish, city))
        thread.start()
        
        
        return render_template('index.html', loading=True, dish=dish, city=city)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False) 

