variable "project_id" {
  description = "The ID of the Google Cloud project."
  type        = string
}

variable "project_name" {
  description = "The name of the Google Cloud project."
  type        = string
}

variable "billing_account_id" {
  description = "The billing account ID for the Google Cloud project."
  type        = string
}

variable "region" {
  description = "The region for the Google Cloud resources."
  type        = string
  default     = "us-central1" # Optional default value
}

variable "enabled_services" {
  description = "List of Google Cloud services to enable for the project."
  type        = list(string)
  default = [
    "bigquery.googleapis.com",
    "cloudfunctions.googleapis.com",
    "pubsub.googleapis.com",
    "cloudscheduler.googleapis.com"
  ]
}
