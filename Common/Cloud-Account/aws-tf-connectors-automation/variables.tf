# Configure the variables here
 variable "region" {
   type = string
   description = "AWS region"
   default = "us-east-1"
 }

 variable "aws-account-id" {
   type = number
   description = "AWS Account ID"
 }

 variable "c1-id" {
   type = number
   description = "Cloud One External ID or Cloud One Account ID"
 }

  variable "externalid" {
   type = string
   description = "Cloud One External ID or Cloud One Account ID"
   sensitive = true
 }

 variable "policy-prefix" {
   type = string
   description = "IAM policy prefix"
   default = "cloudone-policy-"
 }

 variable "role-prefix" {
   type = string
   description = "IAM role prefix"
   default = "cloudone-role-"
 }

 variable "c1-region" {
   type = string
   description = "Cloud One region"
   default = "us-1"
 }

  variable "ws-account-alias" {
    type = string
    description = "Workload Security Account Alias"
    default = "AWS-Workload-Security"
  }

 variable "c1-api-key" {
  type = string
  description = "Cloud One Api Key"
  sensitive = true
}

 variable "service_token" {
  type = string
  description = "Vision One Service Token"
  sensitive = true
}

