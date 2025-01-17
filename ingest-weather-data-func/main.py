import os
import requests
import datetime
from google.cloud import bigquery


def fetch_weather_data(event, context):
    # Get environment variables
    api_key = os.getenv("WEATHER_API_KEY")
    api_url = os.getenv("WEATHER_API_URL")
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET_ID")
    table_name = os.getenv("BIGQUERY_TABLE_NAME")

    # Validate environment variables
    if not all([api_key, project_id, dataset_id, table_name]):
        raise ValueError("One or more required environment variables are missing.")

    try:
        # Get yesterday's date
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # Fetch weather data from an API
        params = {
            "city": "Chicago",
            "key": api_key,
            "start_date": yesterday,
            "end_date": today.strftime("%Y-%m-%d"),
        }

        # Make API request
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()
        weather_data = response_json["data"][0]

        # Prepare data for BigQuery
        rows_to_insert = [
            {
                "date": weather_data["datetime"],
                "clouds": weather_data.get("clouds"),
                "temperature": weather_data.get("temp"),
                "max_temp": weather_data.get("max_temp"),
                "min_temp": weather_data.get("min_temp"),
                "precipitation": weather_data.get("precip"),
                "snow": weather_data.get("snow"),
                "snow_depth": weather_data.get("snow_depth"),
                "wind_speed": weather_data.get("wind_spd"),
            }
        ]

        # Insert data into BigQuery
        client = bigquery.Client(project=project_id)
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        errors = client.insert_rows_json(table_id, rows_to_insert)

        if errors:
            print(f"Errors occurred while inserting data into BigQuery: {errors}")
        else:
            print(f"Weather data for {yesterday} successfully inserted.")

    except requests.exceptions.RequestException as e:
        # Handle any request-related exceptions (network errors, invalid responses, etc.)
        print(f"Error occurred while fetching weather data: {e}")

    except Exception as e:
        # Catch any other exceptions that were not anticipated
        print(f"An unexpected error occurred: {e}")
