# Outputs
output "network-security-role-name" {
  value = aws_iam_role.network-security-role.name
}
output "network-security-role-arn" {
  value = aws_iam_role.network-security-role.arn
}
output "network-security-name" {
  value = aws_iam_policy.network-security-policy.name
}
output "network-security-arn" {
  value = aws_iam_policy.network-security-policy.arn
}
output "network-security-account-added" {
  value = jsondecode(restapi_object.c1ns-api-call.create_response)
}