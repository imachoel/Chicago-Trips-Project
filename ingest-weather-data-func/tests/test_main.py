import os
import unittest
import pytest
from unittest.mock import patch
from main import fetch_weather_data

class TestWeatherFunction(unittest.TestCase):

    def test_missing_environment_variables(self):
        # Unset the environment variables
        if "WEATHER_API_KEY" in os.environ:
            del os.environ["WEATHER_API_KEY"]
        if "GCP_PROJECT_ID" in os.environ:
            del os.environ["GCP_PROJECT_ID"]
        if "BIGQUERY_DATASET_ID" in os.environ:
            del os.environ["BIGQUERY_DATASET_ID"]
        if "BIGQUERY_TABLE_NAME" in os.environ:
            del os.environ["BIGQUERY_TABLE_NAME"]

        # Check that ValueError is raised due to missing environment variables
        with pytest.raises(ValueError, match="One or more required environment variables are missing."):
            fetch_weather_data(None, None)

    @patch("main.requests.get")
    @patch("main.bigquery.Client.insert_rows_json")
    def test_fetch_weather_data(self, mock_bigquery_client, mock_requests_get):
        os.environ["WEATHER_API_KEY"] = "your_api_key_here"
        os.environ["GCP_PROJECT_ID"] = "your_project_id_here"
        os.environ["BIGQUERY_DATASET_ID"] = "your_dataset_id_here"
        os.environ["BIGQUERY_TABLE_NAME"] = "your_table_name_here"

        # Mock API response
        mock_requests_get.return_value.json.return_value = {
            "main": {"temp": 25},
            "weather": [{"description": "clear sky"}]
        }

        # Mock BigQuery client
        mock_bigquery_client.return_value.insert_rows_json.return_value = []

        # Trigger the function
        fetch_weather_data(None, None)

        # Verify API call
        mock_requests_get.assert_called_once()

if __name__ == "__main__":
    unittest.main()
