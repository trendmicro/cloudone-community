
output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.gcp_region
}

output "service_account" {
  value = google_service_account.cloud_one_conformity_service_account.account_id
}

output "custom_role" {
  value = google_project_iam_custom_role.cloud_one_conformity_access.role_id
}
