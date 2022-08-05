# Select the providers to be use
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.22.0"
    }
    conformity = {
      source = "trendmicro/conformity"
      version = "0.4.5"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.region
}

# Configure the conformity Provider
provider "conformity" {
  region = var.c1-region
  apikey = var.c1-api-key
}