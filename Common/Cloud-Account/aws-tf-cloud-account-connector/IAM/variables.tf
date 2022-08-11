# Configure the variables here
 variable "region" {
   type = string
   description = "AWS region"
   default = "us-east-1"
 }

 variable "aws-account-id" {
   type = string
   description = "AWS Account ID"
   default = "PLEASE_CHANGE_ME"
 }

 variable "aws-account-label" {
   type = string
   description = "AWS Account Label"
   default = "PLEASE_CHANGE_ME"
 }

  variable "aws-account-description" {
   type = string
   description = "AWS Account Description"
   default = "PLEASE_CHANGE_ME"
 }

 variable "externalid" {
   type = string
   description = "Cloud One External ID or Cloud One Account ID"
   default = "PLEASE_CHANGE_ME"
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
   default = "PLEASE_CHANGE_ME"
 }

 variable "c1-api-key" {
   type = string
   description = "Cloud One Api Key"
   default = "PLEASE_CHANGE_ME"
 }