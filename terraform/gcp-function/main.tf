# Create a storage bucket for Cloud Function deployment
resource "google_storage_bucket" "function_bucket" {
  name                        = "${var.project_id}-function-bucket"
  location                    = "US"
  uniform_bucket_level_access = true
}

# Upload the Cloud Function code
resource "google_storage_bucket_object" "function_zip" {
  name   = "function.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = "function.zip"
}

# Create a Pub/Sub topic
resource "google_pubsub_topic" "weather_topic" {
  name = "cron-weather-topic"
}

# Create a Gen 2 Cloud Function triggered by the Pub/Sub topic
resource "google_cloudfunctions2_function" "weather_function" {
  name        = "ingest-weather-data"
  location    = "us-central1"
  build_config {
    runtime     = "python310"
    entry_point = "fetch_weather_data"

    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.function_zip.name
      }
    }
  }

  service_config {
    timeout_seconds    = 300
    environment_variables = {
      WEATHER_API_KEY      = var.weather_api_key
      GCP_PROJECT_ID       = var.project_id
      BIGQUERY_DATASET_ID  = var.bigquery_dataset_id
      BIGQUERY_TABLE_NAME  = var.bigquery_table_name
    }

    # Setting event-driven trigger
    ingress_settings = "ALLOW_ALL" # Adjust based on your network settings
  }

  event_trigger {
    event_type = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.weather_topic.name
  }
}

# Create a Cloud Scheduler job to trigger the Pub/Sub topic at 8 AM daily
resource "google_cloud_scheduler_job" "weather_scheduler" {
  name        = "weather-data-daily-ingestion"
  description = "Trigger Pub/Sub topic for weather data ingestion at 8 AM daily"
  schedule    = "0 8 * * *" # Cron expression for 8 AM daily
  time_zone   = "Etc/UTC"

  pubsub_target {
    topic_name = google_pubsub_topic.weather_topic.id
    data       = base64encode("{\"message\": \"Trigger weather data ingestion\"}")
  }
}

# Ensure required IAM permissions for the Cloud Scheduler
resource "google_project_iam_member" "scheduler_to_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_cloud_scheduler_job.weather_scheduler.name}@gcp-sa-cloudscheduler.iam.gserviceaccount.com"
}