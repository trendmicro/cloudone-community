# Configure the variables here
variable "region" {
  type = string
  description = "AWS region"
  default = "PLEASE_CHANGE_ME"
}

variable "aws-account-label" {
  type = string
  description = "AWS Account Label"
  default = "PLEASE_CHANGE_ME"
}

variable "externalid" {
  type = string
  description = "Cloud One External ID"
  default = "PLEASE_CHANGE_ME"
}

variable "nsaasaccountid" {
  type = string
  description = "Cloud One Network Security NSaaS Account ID"
  default = "852329647234"
}

variable "networksecurityawsaccountid" {
  type = string
  description = "Cloud One Network Security Account ID"
  default = "737318609257"
}

variable "policy-name" {
  type = string
  description = "Cloud One Network Security Policy Name"
  default = "NetworkSecurityPolicy"
}

variable "role-prefix" {
  type = string
  description = "IAM role prefix"
  default = "ns-role-"
}

variable "c1-region" {
  type = string
  description = "Cloud One region"
  default = "PLEASE_CHANGE_ME"
}

variable "c1-api-key" {
  type = string
  description = "Cloud One Api Key"
  default = "PLEASE_CHANGE_ME"
}
