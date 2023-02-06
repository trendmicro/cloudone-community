terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.44.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.2.3"
    }
  }
}
    provider "google" {
      project = var.project_id
      region  = var.gcp_region
    }

    provider "local" {
    }
