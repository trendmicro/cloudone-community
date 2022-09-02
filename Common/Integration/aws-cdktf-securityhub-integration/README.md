# CDK/Terraform project to deploy Cloud One Integrations - AWS Security Hub Connector  

This is a CDKTF project with a pre-generated Terraform template that can be used to deploy all the required IAM resources in a given AWS account to integrate Cloud One Integrations with AWS Security Hub.

## Requirements

Take note of your Cloud One account id.

## Deployment

``` bash
export TF_VAR_awsRegion=YOUR-AWS-REGION
export TF_VAR_securityHubAccountId=YOUR-AWS-ACCOUNT-ID
export TF_VAR_cloudOneAccountId=YOUR-CLOUD-ONE-REGION-ID

cdktf deploy
```
