provider "google" {
  project = var.project_id
  region  = "us-central1"
  credentials = var.gcp-key
}