# Configure the variables here
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