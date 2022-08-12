# Create IAM policy
resource "aws_iam_policy" "network-security-policy" {
  name = var.policy-name
  description = "CloudOne Network Security IAM policy"
  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
            "Action": [
                "ec2:CreateSubnet",
                "ec2:CreateTags",
                "ec2:CreateVpcEndpoint",
                "ec2:DeleteSubnet",
                "ec2:DeleteVpcEndpoints",
                "ec2:DescribeImages",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeVpcs",
                "ec2:DescribeRegions",
                "ec2:DescribeNatGateways",
                "ec2:DescribeSubnets",
                "ec2:DescribeKeyPairs",
                "ec2:DescribeRouteTables",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeVpcEndpoints",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Resource": "*",
            "Effect": "Allow",
            "Sid": "cloudconnectorEc2"
        },
        {
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents"
            ],
            "Resource": "*",
            "Effect": "Allow",
            "Sid": "cloudconnectorCF"
        },
        {
            "Action": [
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetHealth"
            ],
            "Resource": "*",
            "Effect": "Allow",
            "Sid": "cloudconnectorElb"
        },
        {
            "Action": [
                "iam:GetPolicyVersion",
                "iam:GetPolicy"
            ],
            "Resource": "arn:aws:iam::*:policy/${var.policy-name}",
            "Effect": "Allow",
            "Sid": "cloudconnectorIamPolicy"
        },
        {
            "Action": [
                "iam:GetRole",
                "iam:ListAttachedRolePolicies"
            ],
            "Resource": "arn:aws:iam::*:role/${aws_iam_role.network-security-role.name}",
            "Effect": "Allow",
            "Sid": "cloudconnectorIamRole"
        }
  ]
})
    tags = {
    Name = "network-security-policy"
  }
}

# Create IAM role
resource "aws_iam_role" "network-security-role" {
  name_prefix = var.role-prefix
  assume_role_policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::${var.networksecurityawsaccountid}:root",
                    "arn:aws:iam::${var.nsaasaccountid}:root"
                ]
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
    Name = "network-security-role"
  }
}

# Policy Attachment
resource "aws_iam_role_policy_attachment" "iam-role-policy-attachment" {
  depends_on = [aws_iam_role.network-security-role]
  role       = aws_iam_role.network-security-role.name
  policy_arn = aws_iam_policy.network-security-policy.arn
}

# Wait time to sync the IAM
resource "time_sleep" "wait_10_seconds" {
  depends_on = [aws_iam_role_policy_attachment.iam-role-policy-attachment]
  create_duration = "10s"
}