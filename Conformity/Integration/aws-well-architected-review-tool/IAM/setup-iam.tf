# Retrive the external id
data "conformity_external_id" "all"{}

# Create IAM policy
resource "aws_iam_policy" "well-architected-tool-policy" {
  name_prefix = "war-policy-"
  description = "CloudOne Well-Architected IAM policy"
  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "wellarchitected:GetAnswer",
        "wellarchitected:UpdateAnswer"
      ],
      "Resource": var.workload
    }
  ]
})
    tags = {
    Name = "well-architected-tool-policy"
  }
}

# Create IAM role
resource "aws_iam_role" "well-architected-tool-role" {
  name_prefix = "war-role-"
  assume_role_policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::717210094962:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": data.conformity_external_id.all.external_id
        }
      }
    }
  ]
})

  tags = {
    Name = "well-architected-tool-role"
  }
}

# Policy Attachment
resource "aws_iam_role_policy_attachment" "policy-attachment" {
  role       = aws_iam_role.well-architected-tool-role.name
  policy_arn = aws_iam_policy.well-architected-tool-policy.arn
}