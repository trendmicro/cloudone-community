# Outputs
output "well-architected-tool-role-name" {
  value = aws_iam_role.well-architected-tool-role.name
}
output "well-architected-tool-role-arn" {
  value = aws_iam_role.well-architected-tool-role.arn
}
output "well-architected-tool-policy-name" {
  value = aws_iam_policy.well-architected-tool-policy.name
}
output "well-architected-tool-policy-arn" {
  value = aws_iam_policy.well-architected-tool-policy.arn
}