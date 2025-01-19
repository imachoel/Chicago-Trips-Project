import os
import requests
import datetime
from google.cloud import bigquery


def fetch_weather_data(event, context):
    """
    Fetch weather data for the previous day from an external API and insert it into a BigQuery table.

    This function is designed to be triggered by a cloud event (e.g., Google Cloud Function). 
    It retrieves weather data for the city of Chicago for the previous day and inserts the data 
    into a BigQuery table.

    Environment Variables:
    - WEATHER_API_KEY: API key for accessing the weather data API.
    - WEATHER_API_URL: Base URL of the weather API endpoint.
    - GCP_PROJECT_ID: Google Cloud Project ID for the BigQuery client.
    - BIGQUERY_DATASET_ID: Dataset ID in BigQuery.
    - BIGQUERY_TABLE_NAME: Table name in BigQuery.

    Args:
        event: Event payload (not used in this function).
        context: Metadata for the event (not used in this function).

    Raises:
        ValueError: If any required environment variable is missing.
        Exception: For unexpected errors during execution.
    """
    # Step 1: Retrieve environment variables
    api_key = os.getenv("WEATHER_API_KEY")
    api_url = os.getenv("WEATHER_API_URL")
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET_ID")
    table_name = os.getenv("BIGQUERY_TABLE_NAME")

    # Step 2: Validate environment variables
    if not all([api_key, project_id, dataset_id, table_name]):
        raise ValueError("One or more required environment variables are missing.")

    try:
        # Step 3: Calculate the date range for yesterday
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # Step 4: Fetch weather data from the API
        params = {
            "city": "Chicago",  # City for which the weather data is fetched
            "key": api_key,     # API key for authentication
            "start_date": yesterday,  # Start date (yesterday)
            "end_date": today.strftime("%Y-%m-%d"),  # End date (today)
        }

        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()

        # Extract the weather data for yesterday
        weather_data = response_json["data"][0]

        # Step 5: Prepare data for insertion into BigQuery
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

        # Step 6: Insert data into BigQuery
        client = bigquery.Client(project=project_id)
        table_id = f"{project_id}.{dataset_id}.{table_name}"  # Full BigQuery table ID

        errors = client.insert_rows_json(table_id, rows_to_insert)

        if errors:
            print(f"Errors occurred while inserting data into BigQuery: {errors}")
        else:
            print(f"Weather data for {yesterday} successfully inserted.")

    except requests.exceptions.RequestException as e:
        # Step 7: Handle request-related errors
        print(f"Error occurred while fetching weather data: {e}")

    except Exception as e:
        # Step 8: Handle unexpected errors
        print(f"An unexpected error occurred: {e}")
