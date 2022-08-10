# Select the providers to be use
 terraform {
   required_providers {
     aws = {
       source  = "hashicorp/aws"
       version = "~> 4.22.0"
     }
     restapi = {
       source = "Mastercard/restapi"
       version = "1.17.0"
     }
     time = {
       source = "hashicorp/time"
       version = "0.7.2"
     }
   }
 }

 # Configure the AWS Provider
 provider "aws" {
   region = var.region
 }

 provider "restapi" {
   alias                = "restapi_headers"
   uri                  = "https://cloudaccounts.${var.c1-region}.cloudone.trendmicro.com"
   debug                = true
   write_returns_object = true

   headers = {
     Accept = "application/json"
     api-version = "v1"
     Authorization = "ApiKey ${var.c1-api-key}"
   }
 } 