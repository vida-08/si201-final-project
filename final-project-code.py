# SI 201 final project
# Team VMK
# Member 1
    # Name: Weijian Fan (Vida)
    # Student id: 20329072
    # Email: vidafan@umich.edu
# Member 2
    # Name:
    # Student id:
    # Email:
# Member 3
    # Name:
    # Student id:
    # Email:


import json
import requests

def call_api_function(api_key): #Kaz
    # Send requests to all APIs (birds, weather, geocoding)
    # Input: API key needed for authentication (string)
    # Output: A dictionary containing the raw API responses
    pass


def grab_location(latitude, longitude): #Kaz
    # Use the geocoding API to convert a latitude and longitude into a readable location name.
    # Inputs: latitude (float), longitude (float)
    # Outputs: location_name (string)
    pass


def convert_time_stamps(timestanps): #Vida
    # Converts time stamps from birds observation into UNIX time
    # Input: A list/dictionary of timestamp string
    # Output: A list or dictionary of timestamp strings (list of float)
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





