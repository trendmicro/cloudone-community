
# Create Conformity Custom Role
resource "google_project_iam_custom_role" "cloud-one-conformity-access" {
  role_id     = "CloudOneConformityAccess"
  title       = "Cloud One Conformity Access"
  description = "Project level Custom Role for Cloud One Conformity access"
  stage       = "ALPHA"
  permissions = var.permissions
}

# Create Service Account
resource "google_service_account" "cloud-one-conformity-service-account" {
  depends_on = [google_project_iam_custom_role.cloud-one-conformity-access]
  account_id   = "cloud-one-conformity-bot"
  display_name = "Cloud One Conformity Bot"
  description = "GCP Service Account for connecting Cloud One Conformity Bot to GCP"
  project = var.project_id
}

# Grant Service Account Custom Role
resource "google_project_iam_member" "cloud-one-conformity-service-account-attachment" {
  depends_on = [google_project_iam_custom_role.cloud-one-conformity-access, google_service_account.cloud-one-conformity-service-account]
  project = var.project_id
  role    = "roles/${google_project_iam_custom_role.cloud-one-conformity-access.name}"
  member  = "serviceAccount:${google_service_account.cloud-one-conformity-service-account.email}"
}

# Create Service Account Key
resource "google_service_account_key" "cloud-one-conformity-key" {
  depends_on = [google_service_account.cloud-one-conformity-service-account]
  service_account_id = google_service_account.cloud-one-conformity-service-account.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Output Service Account Key
resource "local_file" "myaccountjson" {
    content     = base64decode(google_service_account_key.cloud-one-conformity-key.private_key)
    filename    = "${path.module}/${var.project_id}-${google_service_account.cloud-one-conformity-service-account.name}.json"
}
