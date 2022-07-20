terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.22.0"
    }
  }
}

# Variables
variable "region" {
  type = string
  description = "AWS region"
  default = "PLEASE_CHANGE_ME"
}

variable "workload" {
  type = string
  description = "Well-Architected Workload"
  default = "PLEASE_CHANGE_ME"
}

variable "external-id" {
  type = string
  description = "Cloud One Conformity External Id"
  default = "PLEASE_CHANGE_ME"
}

# Configure the AWS Provider
provider "aws" {
  region = var.region
}


# Create IAM policy
resource "aws_iam_policy" "well-architected-tool-policy" {
  name        = "well-architected-tool-policy"
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
}

# Create IAM role
resource "aws_iam_role" "well-architected-tool-role" {
  name = "well-architected-tool-role"
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
          "sts:ExternalId": var.external-id
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
output "well-architected-toolarn" {
  value = aws_iam_role.well-architected-tool-role.arn
}