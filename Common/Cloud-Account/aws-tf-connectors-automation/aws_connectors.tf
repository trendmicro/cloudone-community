# Wait time to sync the IAM
resource "time_sleep" "wait_20_seconds" {
  create_duration = "20s"
}

locals {
  c1-region = var.c1-region
  c1-api-key = var.c1-api-key
  aws-account-id = var.aws-account-id
}

# Add AWS Workload Security connector
resource "null_resource" "add_ws_connector" {
  depends_on = [time_sleep.wait_20_seconds]
  provisioner "local-exec" {
    command = <<-EOT
      curl -k -s -X POST  https://workload.${var.c1-region}.cloudone.trendmicro.com/api/awsconnectors \
      -H "Authorization: ApiKey ${var.c1-api-key}" \
      -H "api-version: v1" \
      -H "Content-Type: application/json" \
      -d '{ "crossAccountRoleArn": "${aws_iam_role.ws-role.arn}" }' | jq
    EOT
  }
}

# Add the AWS connector
resource "null_resource" "add_aws_connector" {
  depends_on = [time_sleep.wait_20_seconds]
  provisioner "local-exec" {
    command = <<-EOT
      curl -k -s -X POST  https://cloudaccounts.${var.c1-region}.cloudone.trendmicro.com/api/cloudaccounts/aws \
      -H "Authorization: ApiKey ${var.c1-api-key}" \
      -H "api-version: v1" \
      -H "Content-Type: application/json" \
      -d '{ "roleARN": "${aws_iam_role.cloudone-role.arn}" }' | jq
    EOT
  }
}

# Remove the AWS connector on destroy operation
resource "null_resource" "remove_aws_connector" {
  triggers = {
    c1-region = local.c1-region
    c1-api-key = local.c1-api-key
    aws-account-id = local.aws-account-id
  }
  provisioner "local-exec" {
    when = destroy
    command = <<-EOT
      curl -k -s -X DELETE  https://cloudaccounts.${self.triggers.c1-region}.cloudone.trendmicro.com/api/cloudaccounts/aws/${self.triggers.aws-account-id} \
      -H "Authorization: ApiKey ${self.triggers.c1-api-key}" \
      -H "api-version: v1" | jq
    EOT
  }
}

# Remove the AWS Workload Security connector on destroy operation
resource "null_resource" "remove_ws_connector" {
  triggers = {
    c1-region = local.c1-region
    c1-api-key = local.c1-api-key
    aws-account-id = local.aws-account-id
  }
  provisioner "local-exec" {
    when = destroy
    command = <<-EOT
      WSCONNECTORID=(`curl -k -s -X POST  https://workload.${self.triggers.c1-region}.cloudone.trendmicro.com/api/awsconnectors/search \
      -H "Authorization: ApiKey ${self.triggers.c1-api-key}" \
      -H "api-version: v1" \
      -H "Content-Type: application/json" \
      -d '{"maxItems": 1,"searchCriteria": [{"fieldName": "accountId","stringValue": "${self.triggers.aws-account-id}"}]}' | jq '.[][].ID'`)

      curl -k -s -X DELETE  https://workload.${self.triggers.c1-region}.cloudone.trendmicro.com/api/awsconnectors/$WSCONNECTORID \
      -H "api-version: v1" \
      -H "Authorization: ApiKey ${self.triggers.c1-api-key}" | jq
    EOT
  }
}