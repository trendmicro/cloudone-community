
# Create Conformity Custom Role
resource "google_project_iam_custom_role" "cloud_one_conformity_access" {
  role_id     = "CloudOneConformityAccess"
  title       = "Cloud One Conformity Access"
  description = "Project level Custom Role for Cloud One Conformity access"
  permissions = var.permissions
  
}

# Create Service Account
resource "google_service_account" "cloud_one_conformity_service_account" {
  depends_on = [google_project_iam_custom_role.cloud_one_conformity_access]
  account_id   = "cloud-one-conformity-bot"
  display_name = "Cloud One Conformity Bot"
  description = "GCP Service Account for connecting Cloud One Conformity Bot to GCP"
  project = var.project_id
}

# Grant Service Account Custom Role
resource "google_project_iam_member" "cloud_one_conformity_service_account_attachment" {
  depends_on = [google_project_iam_custom_role.cloud_one_conformity_access, google_service_account.cloud_one_conformity_service_account]
  project = var.project_id
  role    = "projects/${var.project_id}/roles/${google_project_iam_custom_role.cloud_one_conformity_access.role_id}"
  member  = "serviceAccount:${google_service_account.cloud_one_conformity_service_account.email}"
}

# Create Service Account Key
resource "google_service_account_key" "cloud_one_conformity_key" {
  depends_on = [google_service_account.cloud_one_conformity_service_account]
  service_account_id = google_service_account.cloud_one_conformity_service_account.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Output Service Account Key
resource "local_file" "myaccountjson" {
    content     = base64decode(google_service_account_key.cloud_one_conformity_key.private_key)
    filename    = "gcp-key.json"
}
