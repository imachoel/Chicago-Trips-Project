import os
import traceback
import requests
from google.cloud import bigquery


def fetch_and_insert_bulk_weather_data():
    """
    Fetch weather data from an external API and insert it into a BigQuery table.

    Environment Variables:
    - WEATHER_API_KEY: API key for accessing the weather data API.
    - WEATHER_API_URL: Base URL of the weather API endpoint.
    - GCP_PROJECT_ID: Google Cloud Project ID for the BigQuery client.
    - BIGQUERY_DATASET_ID: Dataset ID in BigQuery.
    - BIGQUERY_TABLE_NAME: Table name in BigQuery.

    Raises:
        ValueError: If any required environment variable is missing.
        Exception: For unexpected errors during execution.
    """
    # Step 1: Retrieve configuration from environment variables
    api_key = os.getenv("WEATHER_API_KEY")
    api_url = os.getenv("WEATHER_API_URL")
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET_ID")
    table_name = os.getenv("BIGQUERY_TABLE_NAME")

    # Step 2: Validate environment variables
    if not all([api_key, project_id, dataset_id, table_name, api_url]):
        raise ValueError("One or more required environment variables are missing.")

    try:
        # Step 3: Define the date range and API parameters
        params = {
            "city": "Chicago",  # City for which the weather data is fetched
            "key": api_key,     # API key for authentication
            "start_date": "2023-06-01",  # Start date of the weather data range
            "end_date": "2023-12-31",    # End date of the weather data range
        }

        # Fetch weather data from the API
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()

        # Extract the weather data list from the API response
        weather_data_list = response_json["data"]

        # Step 4: Initialize BigQuery client and prepare rows for insertion
        client = bigquery.Client(project=project_id)
        table_id = f"{project_id}.{dataset_id}.{table_name}"  # Full BigQuery table ID

        rows_to_insert = []
        for weather_data in weather_data_list:
            # Map API response fields to table schema
            rows_to_insert.append(
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
            )

        # Step 5: Perform bulk insert into BigQuery
        errors = client.insert_rows_json(table_id, rows_to_insert)

        if errors:
            print(f"Errors occurred during bulk insertion: {errors}")
        else:
            print(
                f"Successfully inserted {len(rows_to_insert)} rows into {table_id}."
            )

    except requests.exceptions.RequestException as e:
        # Handle API request-related errors
        print(f"Error occurred while fetching weather data: {e}")

    except Exception as e:
        # Log unexpected errors
        traceback.print_exc()
        print(f"An unexpected error occurred: {e}")
