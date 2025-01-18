variable "project_id" {
  description = "The GCP project ID where the function will be deployed."
}

variable "weather_api_key" {
  description = "API key for the weather API."
  sensitive   = true
}

variable "bigquery_dataset_id" {
  description = "BigQuery dataset ID for storing weather data."
}

variable "bigquery_table_name" {
  description = "BigQuery table name for storing weather data."
}