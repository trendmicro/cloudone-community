# Add AWS Account to Cloud One

 To set up a new Cloud Account, you must deploy resources in your AWS account to provide access to Trend Micro Cloud One. You can deploy the Terraform template, which will create the required AWS resources.

 ## Requirements

 - Have a [Cloud One](https://www.trendmicro.com/cloudone) account. [Sign up for a free trial now](https://cloudone.trendmicro.com/register) if it's not already the case!
 - An AWS Account with Admin permissions
 - AWS CLI [installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

 ## Setup IAM Permissions

 To setup the IAM permission I've create a terraform template that you can use, it will create the policy, role and the attachment between them, first clone the repository to your machine and access the folder of this project, here the commands to deploy the permissions via terraform:

 To install terraform, follow this [Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli#install-terraform)

 First you need to provide in the terraform template (variables.tf file):
   - Cloud One External ID (The same as Cloud One Account ID)
   - AWS Region
   - AWS Account ID
   - AWS Account Label
   - AWS Account Description
   - Cloud One Region

 Then you can execute the following:

   ```
   cd IAM
   terraform init
   terraform plan -out=plan
   terraform apply -auto-approve
   ```

   ## Make a API call with Curl

   At this moment, to add the account to cloudone is only available on the api, to make the api call yourself use command below to use the API to add the account:

   ```bash
   curl -X POST https://cloudaccounts.{region}.cloudone.trendmicro.com/api/cloudaccounts/aws \
     -H 'Authorization: ApiKey <YOUR-CLOUDONE-API-KEY>' \
     -H 'api-version: v1' \
     -H 'Content-Type: application/json' \
     -d '{ "alias": "<YOUR-AWS-ACCOUNT-ALIAS>", "description": "<YOUR-AWS-ACCOUNT-DESCRIPTION>", "roleARN": "<YOUR-IAM-ROLE-ARN>" }'
   ```

   You should see a message like this:

   ```json
  {
    "id": "012345678910",
    "roleARN": "arn:aws:iam::012345678910:role/role-name",
    "created": "2020-07-10T07:02:10Z",
    "lastModified": "2020-07-10T07:02:10Z",
    "alias": "production account",
    "description": "Corp ABC production account",
    "state": "managed"
  }
   ```

In the future when is available through the UI, use the `roleARN` value printed by the terraform template.

**Note:** For more information about the api call, refer to the [Documentation](https://cloudone.trendmicro.com/docs/cloud-account-management/api-reference/tag/AWS).