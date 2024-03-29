# Well-Architected Conformity Sync

This tool sets up a one-way synchronization link between Cloud One Conformity and a AWS Well-Architected review of your choice.

The sync populates the 'Notes' field with a summary of Conformity findings. This summary helps determine whether a workload is applying the best practices effectively.

The sync works only by demand; if any configurations were remediated between runs you will need to run it again **but keep in mind that existing notes will be over-written.**

For further details, see the resources below:

- See [AWS Well Architected Tool](https://cloudone.trendmicro.com/docs/conformity/aws-integration/#aws-well-architected-tool) for further details about Conformity's integration with the Well Architected tool.

- See [Conformity Well Architected API](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Well-Architected-Tool) for further details about the Conformity WellArchitected sync API.

## Pre-requisites

- Administrator access to the AWS Console. In default, sufficient access rights to run CloudFormation templates and to invoke Lambda functions from the [AWS CLI](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) or [AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html)
- AWS Account Id
- Ensure the [workload has been defined](https://docs.aws.amazon.com/wellarchitected/latest/userguide/define-workload.html) in the AWS Well Architected tool
- Have the following information available:
  - [**Cloud One Account Id**](https://cloudone.trendmicro.com/docs/cloud-account-management/aws/#cloud-account-page)
  - [**Cloud One Conformity External Id**](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/External-IDs)
  - [**Cloud One API Key**](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) with Full Access (Admin)
  - [**Cloud One Conformity AWS Account Id**](https://cloudone.trendmicro.com/docs/cloud-account-management/aws/#cloud-account-page)

## Installation

There are two options for installing this integration:

### Console Installation

- Log in to your [AWS Console](https://console.aws.amazon.com/)
- Create the AWS CloudFormation Stack `Conformity-WellArchitected-sync` using `conformity-wellarchitected-sync.yaml`
- Provide the information in the Pre-requisites section above.

### CLI Installation

- Step 1: Run the `configure-stack.py` script with the appropriate values:
  `configure-stack.py [-h] --accountId ACCOUNTID --region {trend-us-1,us-1,au-1,ie-1,sg-1,in-1,jp-1,ca-1,de-1} --apiKey APIKEY --conformityAccountId CONFORMITYACCOUNTID --externalId EXTERNALID --owner OWNER --environment ENVIRONMENT`
- Step 2: Run the `sync.py` script with the appropriate values:
  `sync.py [-h] [--stackName STACKNAME] --workloadArn WORKLOADARN`

Note: Step #2 is the 'sync'. Invoke it to update the well-architected review of your choice.

## Resources

The sync tool will set up the following resources in your AWS account:

- 3 AWS SSM Parameters
- 1 AWS Secrets Manager Secret
- 3 AWS IAM Customer-managed Policies
- 2 AWS IAM Roles
- 1 AWS Lambda Function

## Questions, Commentaries or Improvements

Raise an issue, question or PR.
