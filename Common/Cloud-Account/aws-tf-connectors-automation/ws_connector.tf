# Create IAM policy
resource "aws_iam_policy" "ws-policy" {
  name_prefix = "ws-policy-"
  description = "Workload Security Policy"
  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
                "ec2:DescribeImages",
                "ec2:DescribeInstances",
                "ec2:DescribeRegions",
                "ec2:DescribeSubnets",
                "ec2:DescribeTags",
                "ec2:DescribeVpcs",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeSecurityGroups",
                "workspaces:DescribeWorkspaces",
                "workspaces:DescribeWorkspaceDirectories",
                "workspaces:DescribeWorkspaceBundles",
                "workspaces:DescribeTags",
                "iam:ListAccountAliases",
                "iam:GetRole",
                "iam:GetRolePolicy",
                
      ],
      "Effect": "Allow",
              "Resource": [
                "*"
              ]
      "Sid": "cloudconnector"
    }
  ]
})
    tags = {
    Name = "Workload Security Policy"
  }
}

# Create IAM role
resource "aws_iam_role" "ws-role" {
  name_prefix = "ws-role-"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "147995105371"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": var.externalid
                }
            }
        }
    ]
})

  tags = {
    Name = "Workload Security Role"
  }
}

# Policy Attachment
resource "aws_iam_role_policy_attachment" "role-ws-attachment" {
  role       = aws_iam_role.ws-role.name
  policy_arn = aws_iam_policy.ws-policy.arn
}