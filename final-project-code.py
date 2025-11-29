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
    # Name: Mizuki Kuno
    # Student id:78832653
    # Email: mizuki@umich.edu


import json
import requests
import re
import unittest
import os
from datetime import datetime, timezone
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_NAME = os.path.join(BASE_DIR, "final_project.db")

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
    except:
        print(f"Error calling eBird API")
        return None
    
def call_weather_api(latitude, longitude, timestamp): #Kaz
    # Call the Open-Meteo Archive API to get historical weather data for a specific location and time
    # Input: latitude (float), longitude (float), timestamp (int - Unix time)
    # Output: A dictionary containing formatted weather data, or None if error
    # Note: Open-Meteo is free and doesn't require an API key
    
    # Convert Unix timestamp to date string (YYYY-MM-DD)
    from datetime import datetime
    dt = datetime.utcfromtimestamp(int(timestamp))
    date_str = dt.strftime('%Y-%m-%d')
    
    # Open-Meteo Archive API URL (no timezone parameter, uses GMT by default)
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={date_str}&end_date={date_str}&daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract data from the response
        if 'daily' in data and data['daily']:
            daily = data['daily']
            
            # Return formatted dictionary
            return {
                'latitude': latitude,
                'longitude': longitude,
                'date': date_str,
                'temperature_mean': daily['temperature_2m_mean'][0] if daily.get('temperature_2m_mean') else None,
                'temperature_max': daily['temperature_2m_max'][0] if daily.get('temperature_2m_max') else None,
                'temperature_min': daily['temperature_2m_min'][0] if daily.get('temperature_2m_min') else None,
                'unix_timestamp': timestamp
            }
        else:
            print(f"No weather data found in API response")
            return None
    except:
        print(f"Error calling Open-Meteo Archive API")
        return None


def grab_location(latitude, longitude): #Kaz
    # Use the geocoding API to convert a latitude and longitude into a readable location name.
    # Inputs: latitude (float), longitude (float)
    # Outputs: location_name (string)
    
    api_keys = get_api_keys()
    api_key = api_keys.get('OPENWEATHER_API_KEY')
    
    if not api_key:
        print("Error: OPENWEATHER_API_KEY not found in api_keys.txt")
        return None
    
    url = f'http://api.openweathermap.org/geo/1.0/reverse?lat={latitude}&lon={longitude}&limit=1&appid={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            location = data[0]
            # Construct a readable location name from the response
            # Response structure: [{"name": "City", "country": "GB", "state": "State", ...}]
            name = location.get('name', '')
            country = location.get('country', '')   
            
            # Build location string: "City, Country"
            if name and country:
                location_name = f"{name}, {country}"
            elif name:
                location_name = name
            elif country:
                location_name = country
            else:
                location_name = "Unknown"
            
            return location_name
        else:
            print("No location found for the given coordinates")
            return None
    except:
        print(f"Error calling OpenWeather Geocoding API")
        return None


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

# def clean_bird_data(raw_bird_data): #Vida
#     # Clean and process raw bird observation data from the API.
#     # Inputs: raw data from API
#     # Outputs: cleaned/processed data ready for database insertion
#     if not raw_bird_data:
#         return []

#     cleaned = []

#     for obs in raw_bird_data:
#         unix_time = convert_time_stamps(obs.get("obsDt"))

#         lat = obs.get("lat")
#         lng = obs.get("lng")

#         # Reverse geocoding
#         location_name = None
#         if lat is not None and lng is not None:
#             location_name = grab_location(lat, lng)

#         cleaned.append({
#             "speciesCode": obs.get("speciesCode"),
#             "comName": obs.get("comName"),
#             "sciName": obs.get("sciName"),
#             "locId": obs.get("locId"),
#             "locName": obs.get("locName"),
#             "loc_standardized": location_name,
#             "latitude": lat,
#             "longitude": lng,
#             "obsDt": obs.get("obsDt"),
#             "unix_time": unix_time,
#             "howMany": obs.get("howMany"),
#             "subId": obs.get("subId"),
#         })

#     return cleaned

    

def create_bird_database(raw_bird_data, db_name=DB_NAME, max_rows_per_run=20): #Vida
    # Create SQLite database tables to store cleaned API data.
    # Inputs: processed/cleaned data from API
    # Outputs: database connections or paths

    # Stores cleaned bird data in a database in a rubric-compliant way:
    # Inserts NO MORE THAN 25 new items per run.
    # Prevents duplicate rows using unique constraints + OR IGNORE.
    # Creates 2 tables that share an integer key:
    #     1. locations (id INTEGER PRIMARY KEY, name TEXT UNIQUE, lat, lon)
    #     2. bird_observations (references locations.id)
    # Only process the first N rows (required by rubric)
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # TABLE 1: LOCATIONS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loc_name TEXT UNIQUE,
            latitude REAL,
            longitude REAL
        )
    """)

    # TABLE 2: BIRD OBSERVATIONS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bird_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species_code TEXT,
            com_name TEXT,
            sci_name TEXT,
            location_id INTEGER,
            obs_dt TEXT,
            obs_unix_timestamp REAL,
            how_many INTEGER,
            sub_id TEXT,
            UNIQUE(species_code, obs_dt, location_id),
            FOREIGN KEY(location_id) REFERENCES locations(id)
        )
    """)

    inserted = 0

    for obs in raw_bird_data:

        if inserted >= max_rows_per_run:
            break

        lat = obs.get("lat")
        lon = obs.get("lng")
        obs_dt = obs.get("obsDt")
        unix_ts = convert_time_stamps(obs_dt)

        if lat is None or lon is None:
            continue

        # Get location name from coordinates using grab_location
        loc_name = grab_location(lat, lon)
        
        if not loc_name:
            continue

        # Insert location (will be ignored if loc_name already exists)
        cur.execute("""
        INSERT OR IGNORE INTO locations (loc_name, latitude, longitude)
        VALUES (?, ?, ?)
        """, (loc_name, lat, lon))

        # Retrieve location_id by loc_name
        cur.execute("""
            SELECT id FROM locations
            WHERE loc_name = ?
        """, (loc_name,))
        row = cur.fetchone()
        if not row:
            continue
        location_id = row[0]

        # Insert bird observation
        cur.execute("""
            INSERT OR IGNORE INTO bird_observations (
                species_code, com_name, sci_name,
                location_id, obs_dt, obs_unix_timestamp,
                how_many, sub_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            obs.get("speciesCode"),
            obs.get("comName"),
            obs.get("sciName"),
            location_id,
            obs_dt,
            unix_ts,
            obs.get("howMany"),
            obs.get("subId")
        ))

        if cur.rowcount > 0:
            inserted += 1

    conn.commit()
    conn.close()
    return db_name
    pass

def count_location_rows(db_name=DB_NAME, table_name="locations"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    conn.close()
    return count

def load_until_target(region="US", target=120):
    while True:
        current = count_location_rows()
        print(f"Current rows in locations table: {current}")

        if current >= target:
            print(f"Reached {target} unique locations! Stopping.")
            break

        print("Fetching new bird observations from eBird...")
        raw = call_bird_api(region)
        create_bird_database(raw)

    pass

def weather_until_target(target=120):
    
    pass


def create_weather_table(weather_data): #Mizuki
    # Create table in the main database.
    # Inputs: processed/cleaned data from API
    # Outputs: database connections or paths
    db_path = os.path.join(BASE_DIR, DB_NAME)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create weather table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            date TEXT,
            temperature_mean REAL,
            temperature_max REAL,
            temperature_min REAL,
            unix_timestamp REAL
        )
    """)
    
    # Insert weather data if provided
    if weather_data:
        for weather in weather_data:
            # Check if this record already exists (avoid duplicates)
            cur.execute("""
                SELECT id FROM weather_data 
                WHERE latitude = ? AND longitude = ? AND date = ?
            """, (
                weather.get('latitude'),
                weather.get('longitude'),
                weather.get('date')
            ))
            
            if cur.fetchone() is None:
                cur.execute("""
                    INSERT INTO weather_data 
                    (latitude, longitude, date, temperature_mean, temperature_max, 
                     temperature_min, unix_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    weather.get('latitude'),
                    weather.get('longitude'),
                    weather.get('date'),
                    weather.get('temperature_mean'),
                    weather.get('temperature_max'),
                    weather.get('temperature_min'),
                    weather.get('unix_timestamp')
                ))
    
    conn.commit()
    conn.close()
    
    return db_path
    pass


def create_land_water_table(land_water_data): #Kaz
    # Create table in the main database
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
    # Test the geocoding API
    print("Testing OpenWeather Geocoding API...")
    latitude = 51.5098
    longitude = 0.1180
    location = grab_location(latitude, longitude)
    
    if location:
        print(f"\nLocation for ({latitude}, {longitude}): {location}")
    else:
        print("Failed to retrieve location")
    
    print("\n" + "="*50 + "\n")
    
    # Test the weather API
    print("Testing OpenWeather Timemachine API...")
    weather_lat = 39.099724
    weather_lon = -94.578331
    weather_dt = 1643803200
    weather_data = call_weather_api(weather_lat, weather_lon, weather_dt)
    
    if weather_data:
        print(f"\nRetrieved weather data for ({weather_lat}, {weather_lon}) at timestamp {weather_dt}")
        print(f"\nWeather data keys: {list(weather_data.keys())}")
        if 'data' in weather_data and len(weather_data['data']) > 0:
            print(f"\nFirst data point:")
            print(json.dumps(weather_data['data'][0], indent=2))
    else:
        print("Failed to retrieve weather data")
    
    print("\n" + "="*50 + "\n")
    
    # Test the bird API
    print("Testing eBird API...")
    bird_data = call_bird_api("US")
    
    if bird_data:
        print(f"\nRetrieved {len(bird_data)} bird observations")
        print("\nFirst observation:")
        print(json.dumps(bird_data[0], indent=2))
    else:
        print("Failed to retrieve bird data")
    
    
    print("\nCreating database...")
    db_path = create_bird_database(bird_data)

    if db_path:
        print(f"Database created successfully at: {db_path}")
    else:
        print("Failed to create bird database")

    # Additional check: count rows to confirm insertion
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Count rows in locations table
        cur.execute("SELECT COUNT(*) FROM locations")
        loc_count = cur.fetchone()[0]

        # Count rows in bird_observations table
        cur.execute("SELECT COUNT(*) FROM bird_observations")
        obs_count = cur.fetchone()[0]

        print(f"\nDatabase check:")
        print(f"-Locations table contains: {loc_count} rows")
        print(f"-Bird observations table contains: {obs_count} rows")

        conn.close()

    except Exception as e:
        print(f"Error verifying database: {e}")
    
    # loop until we have 120 rows for location table)
    print("Loading bird data until 120 unique locations are reached...")
    load_until_target(region="US", target=120)
    print("Done!")
    
    # Uncomment to run unit tests instead
    # unittest.main(verbosity=2)


