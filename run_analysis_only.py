import os
from pathlib import Path
from analyzers.ranker import analyze_and_rank

# Set up data directory
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

# This script allows you to run the analysis part of the pipeline
# on any existing raw data JSON file, without needing to run the web app
# or the scraper.

def main():
    """
    Main function to prompt user for input and run the analysis.
    """
    print("--- 🍜 Offline Food Rank Analyzer 🍜 ---")
    
    # Ask the user which data they want to analyze
    dish_input = input("Enter the dish for the data you want to analyze (e.g., dosa, biryani): ").strip().lower()
    city_input = input("Enter the city for the data you want to analyze (e.g., bengaluru): ").strip().lower()

    if not dish_input or not city_input:
        print("Error: Both dish and city must be provided.")
        return

    # Construct the expected filename from the user's input
    clean_dish = dish_input.replace(" ", "_")
    clean_city = city_input.replace(" ", "_")
    raw_data_filename = DATA_DIR / f"data_{clean_dish}_{clean_city}.json"

    print("-" * 30)
    
    # Check if the required data file actually exists
    if raw_data_filename.exists():
        print(f"Found data file: '{raw_data_filename}'")
        print("Starting analysis and ranking process...")
        
        # Call the existing, powerful analysis function
        analyze_and_rank(
            data_filename=raw_data_filename,
            dish=dish_input,
            city=city_input
        )
    else:
        print(f"Error: Could not find the required data file '{raw_data_filename}'.")
        print("Please make sure the file exists in your project directory.")

if __name__ == "__main__":
    main()
