# Select the providers to be use
 terraform {
   required_providers {
     aws = {
       source  = "hashicorp/aws"
       version = "~> 4.22.0"
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