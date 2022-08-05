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

# Variables
variable "region" {
  type = string
  description = "AWS region"
  default = "PLEASE_CHANGE_ME"
}

variable "c1-region" {
  type = string
  description = "Cloud One region"
  default = "PLEASE_CHANGE_ME"
}

variable "workload" {
  type = string
  description = "Well-Architected Workload"
  default = "PLEASE_CHANGE_ME"
}

variable "c1-api-key" {
  type = string
  description = "Cloud One Api Key"
  default = "PLEASE_CHANGE_ME"
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

# Retrive the external id
data "conformity_external_id" "all"{}

# Create IAM policy
resource "aws_iam_policy" "well-architected-tool-policy" {
  name_prefix = "war-policy-"
  description = "CloudOne Well-Architected IAM policy"
  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "wellarchitected:GetAnswer",
        "wellarchitected:UpdateAnswer"
      ],
      "Resource": var.workload
    }
  ]
})
    tags = {
    Name = "well-architected-tool-policy"
  }
}

# Create IAM role
resource "aws_iam_role" "well-architected-tool-role" {
  name_prefix = "war-role-"
  assume_role_policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::717210094962:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": data.conformity_external_id.all.external_id
        }
      }
    }
  ]
})

  tags = {
    Name = "well-architected-tool-role"
  }
}

# Policy Attachment
resource "aws_iam_role_policy_attachment" "policy-attachment" {
  role       = aws_iam_role.well-architected-tool-role.name
  policy_arn = aws_iam_policy.well-architected-tool-policy.arn
}

# Output
output "well-architected-tool-role-name" {
  value = aws_iam_role.well-architected-tool-role.name
}
output "well-architected-tool-role-arn" {
  value = aws_iam_role.well-architected-tool-role.arn
}
output "well-architected-tool-policy-name" {
  value = aws_iam_policy.well-architected-tool-policy.name
}
output "well-architected-tool-policy-arn" {
  value = aws_iam_policy.well-architected-tool-policy.arn
}