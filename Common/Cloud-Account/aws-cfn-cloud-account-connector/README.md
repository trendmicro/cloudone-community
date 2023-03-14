# Add AWS Account to Cloud One

To fully integrate an AWS account in Cloud One, you must deploy resources in your AWS account and do manual steps in TrendCloud One dashboard. This CloudFormation template automates all these steps on your behalf, including integrating it to Vision One.

## Requirements

- Have an API Key for a [Cloud One](https://www.trendmicro.com/cloudone) account. [Sign up for a free trial now](https://cloudone.trendmicro.com/register) if it's not already the case!
- An AWS Account with Admin permissions
- Generate a Vision One Enrollment Token.
- An S3 Bucket that's already configured as a destination for a Trail.

## Limitations

- Your Stack name must be up 8 characters long or shorter. I recommend `CloudOne`.
- You must deploy the stack to the following region based on your Cloud One account region:

| Cloud One Region  | AWS Region      |
| ----------------- | --------------- |
| us-1              | us-east-1       |
| in-1              | ap-south-1      |
| gb-1              | eu-west-2       |
| au-1              | ap-southeast-2  |
| de-1              | eu-central-1    |
| jp-1              | ap-northeast-1  |
| sg-1              | ap-southeast-1  |
| ca-1              | ca-central-1    |

## Deployment

### Via Dashboard

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=CloudOne&templateURL=https://cloudone-community.s3.us-east-1.amazonaws.com/latest/Common/Cloud-Account/aws-cfn-cloud-account-connector/main.template.yaml)

### Via CLI

You can run the following:

```bash
#!/bin/bash
export BUCKET="your-cloudtrail-bucket"
export APIKEY="your-cloudone-apikey"
export TOKEN="your-visionone-enrollment-token"
aws cloudformation create-stack --stack-name common-onboard-test --template-url https://cloudone-community.s3.us-east-1.amazonaws.com/latest/Common/Cloud-Account/aws-cfn-cloud-account-connector/main.template.yaml --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --parameters ParameterKey=ExistingCloudtrailBucketName,ParameterValue=$BUCKET ParameterKey=CloudOneApiKey,ParameterValue=$APIKEY ParameterKey=VisionOneServiceToken,ParameterValue=$TOKEN ParameterKey=QSS3KeyPrefix,ParameterValue=$HASH/
```
