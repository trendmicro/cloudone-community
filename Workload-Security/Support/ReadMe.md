# Trend Workload Security - Agent Diagnostic Collection Tool for AWS SSM

This tool is intended to aid in generating and collecting the workload security agent diagnostic log package.
The output of this tool can be provided to Trend Micro Support on case creation.

---

## Requirements for use.

### SSM Automation Operations IAM Role
- Create an IAM Role for SSM Automations to Assume to execute document. See example [SSM-Policy](https://github.com/JustinDPerkins/TrendCloudOne-SupportCollection/blob/main/Workload-Security/aws/ssm-iam-example-policy.json)
- The IAM Role requires SSM to be a Trusted Entity.

### Instance Requirements:
- Requires the Workload Security Agent to be deployed on instance.
- Requires the SSM Agent to be Installed and Running. See [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html)
- The EC2 Instance requires an IAM Role with [AWS SSMManagedCore permissions](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonSSMManagedInstanceCore.html).
- The EC2 will need an IAM Role with S3:PutObject permissions to upload the agent diagnostic package to S3.
- The Instance will require the AWS CLI to be installed. See [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

### Designated Logging Bucket
- Requires a new or existing S3 bucket to upload logs to.

---

### Limitations:
- Same Account/Region

---

### What is supported?
- Linux OS
- Windows OS

---
## How Can this tool be used?

### Via AWS Console?
Systems Manager > Documents > All Documents > "Trend-WorkloadSecurity-SupportCollectionTool"
- Provide the ARN value of the SSM Automation Operation IAM Role will assume.(SSM Trusted Entity)
- Provide a single or comma seperated list of Instance ID. (i-1234567890,...,...)
- Provide the Name of the S3 bucket to upload the diagnostic package to.(EC2 will need permissions to this bucket to put objects)

### Via AWS CLI:
- Linux CLI:

```
aws ssm start-automation-execution --document-name "Trend-WorkloadSecurity-SupportCollectionTool" --document-version "\$DEFAULT" --parameters '{"AutomationAssumeRole":["<SSM IAM Automation Role ARN Here>"],"InstanceIds":["<Instance-ID-Here>"],"S3BucketName":["<Bucket-4-Artifact-Name-Here>"]}' --region <region>
```

### Self-Launch
- Navigate to SSM > Documents > Create New > Automation
- Paste the contents of ws-ssm-support-automation.yaml and save.
- Execute Document.
