# Cloud One - Workload Security IAM CDK Stack

The goal of this project is to help Cloud One - Workload Security customers to rapdily deploy the necessary IAM stack to their various AWS account via CDK or, if needed, in CloudFormation after synthesizing it.

## Required Parameters:

 * `ExternalId`                                                     External ID you retrieved from the manager.

## Useful commands

 * `cdk deploy --parameters ExternalId=YOUR_EXTERNAL_ID_HERE`       deploy this stack to your default AWS account/region
 * `cdk synth`                                                      emits the synthesized CloudFormation template
