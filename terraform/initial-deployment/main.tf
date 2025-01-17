provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project" "project" {
  name       = var.project_name
  project_id = var.project_id
  billing_account = var.billing_account_id
}

resource "google_project_service" "services" {
  for_each = toset(var.enabled_services)
  service  = each.value
}
