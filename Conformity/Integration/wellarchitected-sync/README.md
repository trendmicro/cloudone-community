# Well Architected Conformity Sync

This tools sets up a synchronization link between Cloud One Conformity and a AWS Well Architected review.

The sync goes in one direction from Conformity to the AWS Well Architected tool. If configurations are remediated you need to run the synchronization again to update the Well Architected tool **but keep in mind that existing notes will be over-written.**

Setting up the Sync tool creates 2 IAM Roles and their policies, AWS SSM Parameters, a secret and a Lambda function.

See [AWS Well Architected Tool](https://cloudone.trendmicro.com/docs/conformity/aws-integration/#aws-well-architected-tool) for further details about Conformity's integration with the Well Architected tool.

See [Conformity Well Architected API](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Well-Architected-Tool) for further details about the Conformity WellArchitected sync API.

## Pre-requisites

- Administrator access to the AWS Console. In default, sufficient access rights to run CloudFormation templates and to invoke Lambda functions from the [AWS CLI](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) or [AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html)
- Ensure the [workload has been defined](https://docs.aws.amazon.com/wellarchitected/latest/userguide/define-workload.html) in the AWS Well Architected tool
- Have the following information available:
  _ [**Cloud One Account Id**](https://cloudone.trendmicro.com/docs/cloud-account-management/aws/#cloud-account-page)
  _ [**Cloud One Conformity External Id**](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/External-IDs)
  - [**Cloud One API Key**](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) with Full Access (Admin)
  - [**Cloud One Conformity AWS Account Id**](https://cloudone.trendmicro.com/docs/cloud-account-management/aws/#cloud-account-page)

## Installation

There are two options for installing this integration:

### Console Installation

- Log in to your [AWS Console](https://console.aws.amazon.com/)
- Create the AWS CloudFormation Stack `Conformity-WellArchitected-sync` using `conformity-wellarchitected-sync.yaml`

### CLI Installation

- Step 1: Run the `configure-stack.py` script with the appropriate values:
  `configure-stack.py --workload WORKLOAD --accountId ACCOUNTID --region {trend-us-1,us-1,au-1,ie-1,sg-1,in-1,jp-1,ca-1,de-1} --apiKey APIKEY --conformityAccountId CONFORMITYACCOUNTID --externalId EXTERNALID --owner OWNER --environment ENVIRONMENT`
- Step 2: Run the `sync.py` script with the appropriate values:
  `sync.py --stackName STACKNAME`

# Questions, Commentaries or Improvements

Raise an issue, question or PR
