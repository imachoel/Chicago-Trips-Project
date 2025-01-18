resource "google_storage_bucket_object" "function_zip" {
  name   = "function.zip"
  bucket = "${var.project_id}-function-bucket"
  source = "function.zip"
}