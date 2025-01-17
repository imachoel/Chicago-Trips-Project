import os
import traceback
import requests
from google.cloud import bigquery


def fetch_and_insert_bulk_weather_data():
    """
    Fetch weather data from an API and insert it into a BigQuery table.
    """
    # Get environment variables
    api_key = os.getenv("WEATHER_API_KEY")
    api_url = os.getenv("WEATHER_API_URL")
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET_ID")
    table_name = os.getenv("BIGQUERY_TABLE_NAME")


    # Validate environment variables
    if not all([api_key, project_id, dataset_id, table_name, api_url]):
        raise ValueError("One or more required environment variables are missing.")

    try:
        # Define the date range and API parameters
        params = {
            "city": "Chicago",
            "key": api_key,
            "start_date": "2023-06-01",
            "end_date": "2023-12-31",
        }

        # Fetch weather data
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        response_json = response.json()
        weather_data_list = response_json['data']

        # Initialize BigQuery client
        client = bigquery.Client(project=project_id)
        table_id = f"{project_id}.{dataset_id}.{table_name}"

        # Prepare rows for bulk insertion
        rows_to_insert = []
        for weather_data in weather_data_list:
            rows_to_insert.append({
                "date": weather_data["datetime"],
                "clouds": weather_data.get("clouds"),
                "temperature": weather_data.get("temp"),
                "max_temp": weather_data.get("max_temp"),
                "min_temp": weather_data.get("min_temp"),
                "precipitation": weather_data.get("precip"),
                "snow": weather_data.get("snow"),
                "snow_depth": weather_data.get("snow_depth"),
                "wind_speed": weather_data.get("wind_spd"),
            })

        # Perform bulk insert
        errors = client.insert_rows_json(table_id, rows_to_insert)

        if errors:
            print(f"Errors occurred during bulk insertion: {errors}")
        else:
            print(f"Successfully inserted {len(rows_to_insert)} rows into {table_id}.")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching weather data: {e}")

    except ValueError as e:
        print(f"ValueError: {e}")

    except Exception as e:
        traceback.print_exc()
        print(f"An unexpected error occurred: {e}")
