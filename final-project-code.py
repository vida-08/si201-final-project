# SI 201 final project
# Team VMK
# Member 1
    # Name: Weijian Fan (Vida)
    # Student id: 20329072
    # Email: vidafan@umich.edu
# Member 2
    # Name: Kawani Mumtaz
    # Student id: 8517 3732
    # Email: kjmumtaz
# Member 3
    # Name:
    # Student id:
    # Email:


import json
import requests
import re
import unittest
import os
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_api_keys(): #Kaz
    # Hide API keys for security purposes. (like in HW)
    # Input: None
    # Output: A file or dictionary containing hidden API keys

    # Read API keys from a file named 'api_keys.txt'
    # Format:
    # BIRD_API_KEY=your_bird_api_key
    # OPENWEATHER_API_KEY=your_weather_api_key
    
    # Make a file named 'api_keys.txt' in the same directory as this code file before running.
    # It wont sync to the git so its safe.

    try:
        api_keys_path = os.path.join(BASE_DIR, 'api_keys.txt')
        with open(api_keys_path, 'r') as file:
            api_keys = {}
            for line in file:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    api_keys[key.strip()] = value.strip()
            return api_keys
    except FileNotFoundError:
        print(f"Error: api_keys.txt file not found at {api_keys_path}")
        return {}
    except Exception as e:
        print(f"Error reading API keys: {e}")
        return {}
        


def call_api_function(url): #Kaz
    # Send requests to all APIs (birds, weather, geocoding)
    # Input: url needed for authentication (string)
    # Output: A dictionary containing the raw API responses
    pass

def call_bird_api(region_code="KZ"): #Kaz
    # Call the eBird API to get recent bird observations for a specific region
    # Input: region_code (string) - default is "KZ" for Kazakhstan
    # Output: A list of dictionaries containing bird observation data, or None if error
    
    api_keys = get_api_keys()
    api_token = api_keys.get('BIRD_API_KEY')
    
    if not api_token:
        print("Error: BIRD_API_KEY not found in api_keys.txt")
        return None
    
    url = f'https://api.ebird.org/v2/data/obs/{region_code}/recent'
    headers = {
        'X-eBirdApiToken': api_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling eBird API: {e}")
        return None


def grab_location(latitude, longitude): #Kaz
    # Use the geocoding API to convert a latitude and longitude into a readable location name.
    # Inputs: latitude (float), longitude (float)
    # Outputs: location_name (string)
    pass


def convert_time_stamps(timestamps): #Vida
    # Converts ONE timestamp at a time, and the Bird cleaning function loops through all records and converts each individually
    # No need for lists or dictionaries in the converter itself, I feel that will be less buggy
    # Input: timestamp (a string)
    # Output: converted timestamp (a float)
    if not timestamps or timestamps.strip() == "":
        return None

    try:
        dt = datetime.strptime(timestamps, "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None
    pass


def create_bird_database(bird_data): #Vida
    # Create SQLite database tables to store cleaned API data.
    # Inputs: processed/cleaned data from API
    # Outputs: database connections or paths
    pass


def create_weather_database(weather_data): #Mizuki
    # Create SQLite database tables to store cleaned API data.
    # Inputs: processed/cleaned data from API
    # Outputs: database connections or paths
    pass


def create_land_water_database(land_water_data): #Kaz
    # Create SQLite database tables to store cleaned API data.
    # Inputs: processed/cleaned data from API
    # Outputs: database connections or paths
    pass


def calc_total_observations(birds_database, weather_database, land_water_database, location_input): #Kaz
    # Calculate total number of observations in the input location for each location by bird species
    # Outputs: A dictionary summarizing totals
    pass


def calc_land_water_percentage(birds_database, location_input): #Vida
    # Calculate percentage of observations on water/on land for each bird species
    # Output: A dictionary mapping each bird species to its land/water observation percentage.
    pass


def calc_historical_avg_temp(weather_database, birds_database, species_name, location_input,converted_time_stamp): #Mizuki
    # Compute historical average temperatures associated with sightings of a migratory bird species by matching bird observation timestamps to corresponding weather data.
    # Output: a dictionary
    pass


def data_visualization(observation_summary, temperature_summary, land_water_percentage): #Vida
    # Generate charts (line/ bar/ scatter) using Seaborn based on calculations
    # Output: Visual files saved to project directory (e.g., .png graphs)
    pass


def generate_report(): #Mizuki
    # Combine all calculations and visualizations into a single formatted document
    # Input: All computed summaries, saved images from visualization
    pass


def main(): #Kaz
    # Calls all other functions in the correct order.
    # Input: None
    # Output: None
    pass



# Debugging/testing area for any code
class TestCases(unittest.TestCase):
    # for testing convert_time_stamps function
    def test_convert_time_stamps(self):
        self.assertEqual(convert_time_stamps("2020-01-19 10:07"), 1579428420.0)
        self.assertEqual(convert_time_stamps("2017-08-23 10:11"), 1503483060.0)
        self.assertEqual(convert_time_stamps(""), None)
        self.assertEqual(convert_time_stamps("invalid-timestamp"), None)

if __name__ == '__main__':
    # Test the bird API
    print("Testing eBird API...")
    bird_data = call_bird_api("KZ")
    
    if bird_data:
        print(f"\nSuccess! Retrieved {len(bird_data)} bird observations")
        print("\nFirst observation:")
        print(json.dumps(bird_data[0], indent=2))
    else:
        print("Failed to retrieve bird data")
    
    # Uncomment to run unit tests instead
    # unittest.main(verbosity=2)


