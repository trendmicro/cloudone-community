# Outputs
 output "cloudone-role-arn" {
   value = aws_iam_role.cloudone-role.arn
 }
 output "cloudone-policy-part1-arn" {
   value = aws_iam_policy.cloudone-policy-part1.arn
 }
 output "cloudone-policy-part2-arn" {
   value = aws_iam_policy.cloudone-policy-part2.arn
 }
output "ws-role-arn" {
   value = aws_iam_role.ws-role.arn
 }
output "ws-policy-arn" {
   value = aws_iam_policy.ws-policy.arn
 }