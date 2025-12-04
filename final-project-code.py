# SI 201 final project
# Team VMK
# Member 1
    # Name: Weijian Fan (Vida)
    # Student id: 20329072
    # Email: vidafan@umich.edu
# Member 2
    # Name: Kawani Mumtaz
    # Student id: 8517 3732
    # Email: kjmumtaz@umich.edu
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
import matplotlib.pyplot as plt
import seaborn as sns

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
        

def call_bird_api(region_code="US"): #Kaz
    # Call the eBird API to get recent bird observations for a specific region
    # Input: region_code (string) - default is "US" for United States
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
            state = location.get('state', '')
            country = location.get('country', '')   
            
            # Build location string: "City, State, Country" or variations
            if name and state and country:
                location_name = f"{name}, {state}, {country}"
            elif name and country:
                location_name = f"{name}, {country}"
            elif name and state:
                location_name = f"{name}, {state}"
            elif name:
                location_name = name
            elif state and country:
                location_name = f"{state}, {country}"
            elif country:
                location_name = country
            elif state:
                location_name = state
            else:
                location_name = "Unknown"
            
            return location_name
        else:
            print("No location found for the given coordinates")
            return None
    except:
        print(f"Error calling OpenWeather Geocoding API")
        return None


def grab_koeppen(latitude, longitude): #Kaz
    
    url = f'http://climateapi.scottpinkelman.com/api/v1/location/{latitude}/{longitude}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data and 'return_values' in data and len(data['return_values']) > 0:
            climate_data = data['return_values'][0]
            
            return {
                'koeppen_zone': climate_data.get('koppen_geiger_zone'),
                'zone_description': climate_data.get('zone_description')
            }
        else:
            print(f"No Koeppen data found for coordinates ({latitude}, {longitude})")
            return None
    except:
        print(f"Error calling Koeppen Climate API")
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

    
def create_bird_database(raw_bird_data, db_name=DB_NAME, max_rows_per_run=20): #Vida
    # Create SQLite database tables to store cleaned API data.
    # Inputs: data from API
    # Outputs: database connections or paths

    # Creates 2 tables that share an integer key:
    #   1. locations
    #   2. bird_observations
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # TABLE 1: LOCATIONS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loc_name TEXT UNIQUE,
            latitude REAL,
            longitude REAL,
            koeppen_geiger_zone TEXT,
            zone_description TEXT
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
        
        # Get Köppen-Geiger climate data
        koeppen_data = grab_koeppen(lat, lon)
        koeppen_zone = koeppen_data.get('koeppen_zone') if koeppen_data else None
        zone_desc = koeppen_data.get('zone_description') if koeppen_data else None

        # Insert location (will be ignored if loc_name already exists)
        cur.execute("""
        INSERT OR IGNORE INTO locations (loc_name, latitude, longitude, koeppen_geiger_zone, zone_description)
        VALUES (?, ?, ?, ?, ?)
        """, (loc_name, lat, lon, koeppen_zone, zone_desc))

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

def weather_until_complete(db_name=DB_NAME, max_rows_per_run=20):
    # Fetch weather data for all bird observations incrementally
    # Processes up to max_rows_per_run observations at a time until all have weather data
    
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    while True:
        # Count total bird observations
        cur.execute("SELECT COUNT(*) FROM bird_observations")
        total_observations = cur.fetchone()[0]
        
        # Count how many already have weather data (check if table exists first)
        try:
            cur.execute("SELECT COUNT(*) FROM weather_data")
            completed_weather = cur.fetchone()[0]
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            completed_weather = 0
        
        print(f"Weather data progress: {completed_weather}/{total_observations} observations")
        
        if completed_weather >= total_observations:
            print("All bird observations have weather data")
            break
        
        # Get bird observations that don't have weather data yet (up to max_rows_per_run)
        try:
            cur.execute("""
                SELECT bo.id, l.latitude, l.longitude, bo.obs_unix_timestamp
                FROM bird_observations bo
                JOIN locations l ON bo.location_id = l.id
                WHERE bo.id NOT IN (SELECT bird_observation_id FROM weather_data)
                LIMIT ?
            """, (max_rows_per_run,))
        except:
            # If weather_data table doesn't exist, select all bird observations
            cur.execute("""
                SELECT bo.id, l.latitude, l.longitude, bo.obs_unix_timestamp
                FROM bird_observations bo
                JOIN locations l ON bo.location_id = l.id
                LIMIT ?
            """, (max_rows_per_run,))
        
        observations_to_process = cur.fetchall()
        
        if not observations_to_process:
            print("No more observations to process")
            break
        
        # Build list of weather data dictionaries
        weather_data_list = []
        
        for obs_id, lat, lon, timestamp in observations_to_process:
            if timestamp is None:
                print(f"Skipping observation {obs_id} - no timestamp")
                continue
            
            weather_dict = call_weather_api(lat, lon, timestamp)
            
            if weather_dict:
                # Add the bird_observation_id to link the weather data
                weather_dict['bird_observation_id'] = obs_id
                weather_data_list.append(weather_dict)
            else:
                print(f"Failed to get weather data for observation {obs_id}")
        
        # Insert weather data into the database
        if weather_data_list:
            create_weather_table(weather_data_list)
            print(f"Added weather data for {len(weather_data_list)} observations")
        else:
            print("No valid weather data to add")
            break
    
    conn.close()
    pass


def create_weather_table(weather_data, db_name=DB_NAME): #Mizuki
    # Create table in the main database.
    # Inputs: processed/cleaned data from API (list of dicts with bird_observation_id)
    # Outputs: database connections or paths
    
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    # Create weather_data table that references bird_observations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bird_observation_id INTEGER UNIQUE,
            latitude REAL,
            longitude REAL,
            date TEXT,
            temperature_mean REAL,
            temperature_max REAL,
            temperature_min REAL,
            unix_timestamp REAL,
            FOREIGN KEY(bird_observation_id) REFERENCES bird_observations(id)
        )
    """)
    
    inserted = 0
    for weather in weather_data:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO weather_data (
                    bird_observation_id, latitude, longitude, date,
                    temperature_mean, temperature_max, temperature_min, unix_timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                weather.get('bird_observation_id'),
                weather.get('latitude'),
                weather.get('longitude'),
                weather.get('date'),
                weather.get('temperature_mean'),
                weather.get('temperature_max'),
                weather.get('temperature_min'),
                weather.get('unix_timestamp')
            ))
            if cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"Error inserting weather data: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"Inserted {inserted} weather records into database")
    return db_name
    pass


def calc_total_observations(birds_database, location_list): #Kaz
    # Calculate total number of observations for each bird species across inputted locations
    # Inputs: birds_database (path to database), location_list (list of location names)
    # Outputs: A dictionary summarizing totals
    
    conn = sqlite3.connect(birds_database)
    cur = conn.cursor()
    
    # Create placeholders for SQL IN clause
    placeholders = ','.join('?' * len(location_list))
    
    # Query to sum how_many per bird species for the given locations
    cur.execute(f"""
        SELECT bo.com_name, bo.sci_name, SUM(bo.how_many) as total_counts, bo.obs_unix_timestamp
        FROM bird_observations bo
        JOIN locations l ON bo.location_id = l.id
        WHERE l.loc_name IN ({placeholders})
        GROUP BY bo.species_code, bo.com_name, bo.sci_name
        ORDER BY total_counts DESC
    """, location_list)
    
    results = cur.fetchall()
    conn.close()
    
    # Build dictionary with species names as keys and total individuals as values
    observation_summary = {}
    for common_name, scientific_name, total_counts, timestamp in results:

        # Find earliest and latest observation dates for the species
        start_date = min(row[3] for row in results if row[3] is not None)
        end_date = max(row[3] for row in results if row[3] is not None)
        start_date = datetime.utcfromtimestamp(int(start_date)).strftime('%Y-%m-%d')
        end_date = datetime.utcfromtimestamp(int(end_date)).strftime('%Y-%m-%d')

        observation_summary[common_name] = {
            'scientific_name': scientific_name,
            'total_observations': total_counts if total_counts is not None else 0,
            'start_date': start_date,
            'end_date': end_date
        }
    
    return observation_summary
    pass


def calc_climate_type_percentage(birds_database): #Vida
    # Calculate percentage of observations of climate type for birds
    # Output: A dictionary mapping each climate type to the number of observations
    conn = sqlite3.connect(birds_database)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT l.koeppen_geiger_zone, l.zone_description, bo.how_many
        FROM bird_observations bo
        JOIN locations l
        ON bo.location_id = l.id
        WHERE l.koeppen_geiger_zone IS NOT NULL
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return {}
    
    climate_counts = {}
    for code, description, how_many in rows:
        readable_key = f"{code} ({description})"
        count = how_many if how_many is not None else 0
        climate_counts[readable_key] = climate_counts.get(readable_key, 0) + count

    total = sum(climate_counts.values())

    climate_percentages = {}

    for climate, count in climate_counts.items():
        percentage = (count / total) * 100
        climate_percentages[climate] = round(percentage, 2)

    # Adjust for rounding errors to ensure sum equals exactly 100
    if climate_percentages:
        current_sum = sum(climate_percentages.values())
        diff = round(100 - current_sum, 2)
        if diff != 0:
            last_key = list(climate_percentages.keys())[-1]
            climate_percentages[last_key] = round(climate_percentages[last_key] + diff, 2)

    return climate_percentages
    pass


def calc_historical_avg_temp(birds_database, species_name=None): #Mizuki
    # Compute historical average temperatures associated with sightings of a bird species by matching bird observation timestamps to corresponding weather data.
    # Output: a dictionary
    conn = sqlite3.connect(birds_database)
    cur = conn.cursor()
    
    if species_name:
        # Query for a specific species using JOIN
        cur.execute("""
            SELECT bo.com_name, bo.sci_name, 
                   wd.temperature_mean, wd.temperature_max, wd.temperature_min,
                    bo.how_many
            FROM bird_observations bo
            JOIN weather_data wd ON bo.id = wd.bird_observation_id
            WHERE bo.com_name LIKE ?
        """, (f"%{species_name}%",))
    else:
        # Query for all species using JOIN
        cur.execute("""
            SELECT bo.com_name, bo.sci_name, 
                   wd.temperature_mean, wd.temperature_max, wd.temperature_min,
                    bo.how_many
            FROM bird_observations bo
            JOIN weather_data wd ON bo.id = wd.bird_observation_id
        """)
    
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return {}
    
    # Build dictionary to accumulate temperature data per species
    species_temps = {}
    for row in rows:
        com_name, sci_name, temp_mean, temp_max, temp_min, how_many = row
        
        if com_name not in species_temps:
            species_temps[com_name] = {
                'scientific_name': sci_name,
                'temp_means': [],
                'temp_maxs': [],
                'temp_mins': [],
                'how_many': []
            }
        
        if temp_mean is not None:
            species_temps[com_name]['temp_means'].append(temp_mean)
        if temp_max is not None:
            species_temps[com_name]['temp_maxs'].append(temp_max)
        if temp_min is not None:
            species_temps[com_name]['temp_mins'].append(temp_min)
        if how_many is not None:
            species_temps[com_name]['how_many'].append(how_many)
    # Calculate averages for each species
    temperature_summary = {}
    for com_name, data in species_temps.items():
        temp_means = data['temp_means']
        temp_maxs = data['temp_maxs']
        temp_mins = data['temp_mins']
        total_counts = data['how_many']
        
        if temp_means:
            avg_temp = sum(temp_means) / len(temp_means)
            avg_max = sum(temp_maxs) / len(temp_maxs) if temp_maxs else None
            avg_min = sum(temp_mins) / len(temp_mins) if temp_mins else None
            
            temperature_summary[com_name] = {
                'scientific_name': data['scientific_name'],
                'avg_temperature': round(avg_temp, 2),
                'avg_max_temperature': round(avg_max, 2) if avg_max else None,
                'avg_min_temperature': round(avg_min, 2) if avg_min else None,
                'observation_count': sum(total_counts) if total_counts else 0
                
            }
    
    return temperature_summary
    pass


# Data Visualization Functions: 
def obs_summary_bar(observation_summary, loc_name): #Vida
    # Bar chart for total number of observations in the input location for each location by bird species'
    species = list(observation_summary.keys())
    counts = [] 
    for sp in observation_summary:
        info = observation_summary[sp]
        count = info['total_observations']
        counts.append(count)
    
    plt.figure(figsize=(14, 8))

    sns.barplot(
        x=species,
        y=counts,
        hue=species,
        dodge=False,
        legend=False,
        palette="viridis"
    )

    plt.xlabel("Total Observations", fontsize=12)
    plt.ylabel("Bird Species", fontsize=12)
    plt.title(f"Total Bird Observations by Species in {loc_name}", fontsize=14, pad=15)
    plt.suptitle(f"From {observation_summary[species[0]]['start_date']} to {observation_summary[species[0]]['end_date']}", fontsize=10, y=0.92)

    plt.xticks(rotation=90, ha='center', fontsize=8)

    plt.tight_layout()
    plt.show()
    pass

def climate_percentage_pie(climate_type_percentage): #Vida
    # Pie chart for percentage of observations of climate zone for each bird species
    labels = list(climate_type_percentage.keys())
    sizes = list(climate_type_percentage.values())
    colors = sns.color_palette("Set3", n_colors=len(labels))

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_position([-0.15, 0.1, 1.0, 0.8])

    short_labels = [label.split(' ')[0] for label in labels]

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=short_labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        textprops={'fontsize': 6},
    )
    
    ax.legend(wedges, labels, title="Climate Types", loc="center left", bbox_to_anchor=(0.80, 0.5), fontsize=9)

    plt.title("Percentage of Bird Observation Counts by Climate Type")
    plt.axis('equal')
    plt.show()

    pass

def temp_history_scatter(temperature_summary): #Mizuki
    # Scatterplot for the historical average temperatures of observations of a migratory bird’s observational.
    # Input: temperature_summary dictionary from calc_historical_avg_temp
    # Output: Displays scatter plot
    
    if not temperature_summary:
        print("No temperature data to visualize")
        return
    
    species = list(temperature_summary.keys())
    avg_temps = []
    obs_counts = []
    
    for sp in temperature_summary:
        info = temperature_summary[sp]
        avg_temps.append(info['avg_temperature'])
        obs_counts.append(info['observation_count'])
    
    plt.figure(figsize=(12, 8))
    
    scatter = plt.scatter(
        avg_temps,
        obs_counts,
        c=avg_temps,
        cmap='coolwarm',
        s=100,
        alpha=0.7,
        edgecolors='black'
    )
    
    plt.colorbar(scatter, label='Avg Temperature (°C)')
    
    plt.xlabel("Average Temperature (°C)", fontsize=12)
    plt.ylabel("Number of Observations", fontsize=12)
    plt.title("Bird Species: Average Temperature vs Observation Count", fontsize=14, pad=15)
    
    plt.tight_layout()
    plt.show()
    pass

# Extra credit 1 -- Mizuki
def temp_range_bar(temperature_summary): 
    # Bar chart showing temperature range (min to max) for top species
    # Input: temperature_summary dictionary from calc_historical_avg_temp
    # Output: Displays bar chart with error bars
    
    if not temperature_summary:
        print("No temperature data to visualize")
        return
    
    # Sort by observation count and get top 15
    sorted_species = sorted(temperature_summary.items(), 
                           key=lambda x: x[1]['observation_count'], 
                           reverse=True)[:15]
    
    species_names = []
    avg_temps = []
    min_temps = []
    max_temps = []
    
    for sp, info in sorted_species:
        species_names.append(sp[:20])  
        avg_temps.append(info['avg_temperature'])
        min_temps.append(info['avg_min_temperature'] if info['avg_min_temperature'] else info['avg_temperature'])
        max_temps.append(info['avg_max_temperature'] if info['avg_max_temperature'] else info['avg_temperature'])
    
    plt.figure(figsize=(14, 8))
    
    x = range(len(species_names))
    
    # Calculate error bar values
    lower_err = [avg - min_t for avg, min_t in zip(avg_temps, min_temps)]
    upper_err = [max_t - avg for avg, max_t in zip(avg_temps, max_temps)]
    
    plt.bar(x, avg_temps, color='steelblue', alpha=0.8, edgecolor='black')
    plt.errorbar(x, avg_temps, yerr=[lower_err, upper_err], 
                fmt='none', color='darkred', capsize=5, capthick=2)
    
    plt.xticks(x, species_names, rotation=45, ha='right', fontsize=9)
    plt.xlabel("Bird Species", fontsize=12)
    plt.ylabel("Temperature (°C)", fontsize=12)
    plt.title("Temperature Range at Observation Time (Top 15 Species)", fontsize=14, pad=15)
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.show()
    pass

# Extra credit 2 -- Mizuki
def climate_temp_heatmap(birds_database): 
    # Heatmap showing observation counts by climate zone and temperature range
    # Input: birds_database (path to database)
    # Output: Displays heatmap
    
    conn = sqlite3.connect(birds_database)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT l.koeppen_geiger_zone,
               CASE 
                   WHEN wd.temperature_mean < 0 THEN 'Below 0°C'
                   WHEN wd.temperature_mean < 10 THEN '0-10°C'
                   WHEN wd.temperature_mean < 20 THEN '10-20°C'
                   WHEN wd.temperature_mean < 30 THEN '20-30°C'
                   ELSE 'Above 30°C'
               END as temp_range,
               COUNT(*) as count
        FROM bird_observations bo
        JOIN locations l ON bo.location_id = l.id
        JOIN weather_data wd ON bo.id = wd.bird_observation_id
        WHERE l.koeppen_geiger_zone IS NOT NULL AND wd.temperature_mean IS NOT NULL
        GROUP BY l.koeppen_geiger_zone, temp_range
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        print("No data for heatmap")
        return
    
    # Build a dictionary for the heatmap data
    climate_zones = []
    temp_ranges = ['Below 0°C', '0-10°C', '10-20°C', '20-30°C', 'Above 30°C']
    heatmap_data = {}
    
    for zone, temp_range, count in rows:
        if zone not in heatmap_data:
            heatmap_data[zone] = {}
            climate_zones.append(zone)
        heatmap_data[zone][temp_range] = count
    
    # Create matrix for heatmap
    matrix = []
    for zone in climate_zones:
        row = []
        for temp in temp_ranges:
            row.append(heatmap_data[zone].get(temp, 0))
        matrix.append(row)
    
    plt.figure(figsize=(12, 8))
    
    sns.heatmap(matrix, 
                annot=True, 
                fmt='.0f', 
                cmap='YlOrRd',
                xticklabels=temp_ranges,
                yticklabels=climate_zones,
                linewidths=0.5)
    
    plt.xlabel("Temperature Range", fontsize=12)
    plt.ylabel("Köppen Climate Zone", fontsize=12)
    plt.title("Bird Observations: Climate Zone vs Temperature", fontsize=14, pad=15)
    
    plt.tight_layout()
    plt.show()
    pass


def generate_report(observation_summary, temperature_summary, climate_percentage, db_name=DB_NAME): #Mizuki
    # Combine all calculations and visualizations into a single formatted document
    # Input: All computed summaries from calculations
    # Output: Text file with all calculations written out
    
    output_dir = os.path.dirname(db_name)
    if not output_dir:
        output_dir = BASE_DIR
    
    report_path = os.path.join(output_dir, 'calculation_results.txt')
    
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("SI 201 Final Project - Calculation Results\n")
        f.write("Team VMK: Weijian Fan (Vida), Kawani Mumtaz, Mizuki Kuno\n")
        f.write("=" * 70 + "\n\n")
        
        # Section 1: Observation Summary
        f.write("-" * 50 + "\n")
        f.write("SECTION 1: BIRD OBSERVATION COUNTS BY SPECIES\n")
        f.write("-" * 50 + "\n\n")
        
        if observation_summary:
            sorted_obs = sorted(observation_summary.items(), 
                              key=lambda x: x[1]['total_observations'], 
                              reverse=True)
            
            f.write(f"{'Common Name':<35} {'Scientific Name':<35} {'Count'}\n")
            f.write("-" * 80 + "\n")
            
            for common_name, data in sorted_obs:
                f.write(f"{common_name:<35} {data['scientific_name']:<35} {data['total_observations']}\n")
            
            total_species = len(observation_summary)
            total_obs = sum(d['total_observations'] for d in observation_summary.values())
            f.write(f"\nTotal unique species: {total_species}\n")
            f.write(f"Total observations: {total_obs}\n")
        else:
            f.write("No observation data available.\n")
        
        f.write("\n")
        
        # Section 2: Temperature Analysis
        f.write("-" * 50 + "\n")
        f.write("SECTION 2: TEMPERATURE ANALYSIS BY SPECIES\n")
        f.write("-" * 50 + "\n\n")
        
        if temperature_summary:
            sorted_temp = sorted(temperature_summary.items(), 
                               key=lambda x: x[1]['observation_count'], 
                               reverse=True)
            
            f.write(f"{'Species':<30} {'Avg Temp(°C)':<15} {'Min(°C)':<12} {'Max(°C)':<12} {'Observations'}\n")
            f.write("-" * 85 + "\n")
            
            for species, data in sorted_temp:
                avg_temp = f"{data['avg_temperature']:.1f}" if data['avg_temperature'] else "N/A"
                min_temp = f"{data['avg_min_temperature']:.1f}" if data['avg_min_temperature'] else "N/A"
                max_temp = f"{data['avg_max_temperature']:.1f}" if data['avg_max_temperature'] else "N/A"
                f.write(f"{species[:29]:<30} {avg_temp:<15} {min_temp:<12} {max_temp:<12} {data['observation_count']}\n")
            
            # Calculate overall statistics
            all_temps = [d['avg_temperature'] for d in temperature_summary.values() if d['avg_temperature']]
            if all_temps:
                overall_avg = sum(all_temps) / len(all_temps)
                f.write(f"\nOverall average temperature: {overall_avg:.2f}°C\n")
        else:
            f.write("No temperature data available.\n")
        
        f.write("\n")
        
        # Section 3: Climate Zone Analysis
        f.write("-" * 50 + "\n")
        f.write("SECTION 3: CLIMATE ZONE DISTRIBUTION\n")
        f.write("-" * 50 + "\n\n")
        
        if climate_percentage:
            sorted_climate = sorted(climate_percentage.items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)
            
            f.write(f"{'Climate Zone':<40} {'Percentage'}\n")
            f.write("-" * 55 + "\n")
            
            for zone, percentage in sorted_climate:
                f.write(f"{zone:<40} {percentage:.2f}%\n")
        else:
            f.write("No climate zone data available.\n")
        
        f.write("\n")
        f.write("=" * 70 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 70 + "\n")
    
    print(f"Report saved to: {report_path}")
    return report_path
    pass

def request_input_query(query_dict):
    # Request user input for location and species queries
    query_dict['location'] = input("Enter location (e.g., 'Ann Arbor, US'): ").strip()
    query_dict['species'] = input("Enter bird species common name (e.g., 'Bald Eagle') (enter NONE input for all species): ").strip()

    return query_dict


def get_matching_location(input_name, db_name=DB_NAME):
    # Get matching location names from the database based on user input
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("""
        SELECT loc_name FROM locations
        WHERE loc_name LIKE ?
    """, (f"%{input_name}%",))

    results = cur.fetchall()
    conn.close()

    matching_locations = [row[0] for row in results]
    
    return matching_locations


def main(): #Kaz
    # Calls all other functions in the correct order.
    # Input: None
    # Output: None
    

    update_yn = input("Do you want to update the bird database with new observations? (y/n): ").strip().lower()
    
    if update_yn == 'y':

        # Get region code from user input
        region_code = input("Enter region code (e.g., 'US', 'CA', 'GB'): ").strip().upper()
        if not region_code:
            region_code = "US"  # Default to US if no input
            print(f"No region code provided. Using default: {region_code}")
        
        bird_data = call_bird_api(region_code)
        
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
        
        target_X = input("Enter target number of unique locations to load (default 120): ").strip()
        # loop until we have X rows for location table
        print("Loading bird data until target unique locations are reached...")
        load_until_target(region=region_code, target=int(target_X))
        print("Done!")

        print("Loading weather data for all observations...")
        weather_until_complete()
        print("Done!")

        print("Building reports and visualizations...")

    else:
        print("Skipping database update.")
        db_path = DB_NAME

    input_queries = {}
    request_input_query(input_queries)

    matching_locations = get_matching_location(input_queries['location'])
    if not matching_locations:
        print(f"No matching locations found for '{input_queries['location']}'")
        return
    
    # Observation Summary Calculation
    observation_dict = calc_total_observations(db_path, matching_locations)
    print("\nObservation summary calculated.")
    print(observation_dict)

    # Climate Type Summary Calculation
    climate_percentage_dict = calc_climate_type_percentage(DB_NAME)
    print("\nClimate Type Percentage Calculated.")
    print(climate_percentage_dict)

    # Historical Average Temperature Calculation
    temperature_summary_dict = calc_historical_avg_temp(DB_NAME, input_queries['species'])
    print("\nHistorical Average Temperature Summary Calculated.")
    print(temperature_summary_dict)

    # Visualization
    obs_summary_bar(observation_dict, input_queries['location'])
    climate_percentage_pie(climate_percentage_dict)
    temp_history_scatter(temperature_summary_dict)
    temp_range_bar(temperature_summary_dict)
    climate_temp_heatmap(DB_NAME)

    # Generate report
    generate_report(observation_dict, temperature_summary_dict, climate_percentage_dict, DB_NAME)
    
    pass


# Debugging/testing area for any code
class TestCases(unittest.TestCase):
    # for testing convert_time_stamps function
    def test_convert_time_stamps(self):
        self.assertEqual(convert_time_stamps("2020-01-19 10:07"), 1579428420.0)
        self.assertEqual(convert_time_stamps("2017-08-23 10:11"), 1503483060.0)
        self.assertEqual(convert_time_stamps(""), None)
        self.assertEqual(convert_time_stamps("invalid-timestamp"), None)
    
    def test_climate_percentage_calc(self):
        self.assertEqual(sum(calc_climate_type_percentage(DB_NAME).values()), 100)


if __name__ == '__main__':

    main()
    
    # Uncomment to run unit tests instead
    # unittest.main(verbosity=2)


