# Add to Network Security
resource "restapi_object" "c1ns-api-call" {
  depends_on = [time_sleep.wait_10_seconds]
  provider = restapi.restapi_headers
  path = "/api/awsconnectors"
  data = "{ \"accountName\": \"${var.aws-account-alias}\", \"crossAccountRole\": \"${aws_iam_role.network-security-role.arn}\", \"externalId\": \"${var.externalid}\" }"
}