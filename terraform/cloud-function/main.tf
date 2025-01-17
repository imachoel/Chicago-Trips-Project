

resource "google_cloudfunctions_function" "weather_function" {
  name        = "ingest-weather-data"
  runtime     = "python310"
  region      = "us-central1"
  entry_point = "fetch_weather_data"

  source_archive_bucket = google_storage_bucket.function_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip.name

  trigger_http = true
  available_memory_mb = 256

  environment_variables = {
    WEATHER_API_KEY      = var.weather_api_key
    GCP_PROJECT_ID       = var.project_id
    BIGQUERY_DATASET_ID  = var.bigquery_dataset_id
    BIGQUERY_TABLE_NAME  = var.bigquery_table_name
  }
}

resource "google_storage_bucket_object" "function_zip" {
  name   = "function.zip"
  bucket = "${var.project_id}-function-bucket"
  source = "function.zip"
}