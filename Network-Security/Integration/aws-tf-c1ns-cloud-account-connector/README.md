# Add AWS Account to Network Security

Before you can deploy protection on the Network Security management interface, first add a cloud account to allow Network Security to gain access to your cloud account information.

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
  - AWS Account Label
  - Cloud One API Key with `full-access` permissions
  - Cloud One Region

Then you can execute the following:

  ```
  cd IAM
  terraform init
  terraform plan -out=plan
  terraform apply -auto-approve
  ```

  The terraform template will automatically add the AWS account to your Cloud One Network Security using the API, in case you want to do it yourself, delete the file `c1ns.tf` and modify the files `outputs.tf` and `variables.tf` to successfully remove the feature to add automatically the account.
    
  ## Make a API call with Curl

  If you rather to make the api call yourself or to use the UI instead you can follow this [link](https://cloudone.trendmicro.com/docs/network-security/add_cloud_accounts_appliances/) to use the UI or the command below to use the API to add the account:

  ```bash
  curl -X POST https://network.{region}.cloudone.trendmicro.com/api/awsconnectors \
    -H 'Authorization: ApiKey <YOUR-CLOUDONE-API-KEY>' \
    -H 'api-version: v1' \
    -H 'Content-Type: application/json' \
    -d '{ "accountName": "<YOUR-AWS-ACCOUNT-ALIAS>", "crossAccountRole": "<YOUR-IAM-ROLE-ARN>", "externalId": "<YOUR-CLOUDONE-EXTERNAL-ID>" }'
  ```

  You should see a message like this:

  ```json
  {
  "id": 1136072878564,
  "accountId": "136072877735",
  "accountName": "My AWS Account",
  "crossAccountRole": "arn:aws:iam::136072877735:role/ns-role-8214871892417248124",
  "externalId": "855270469588"
}
  ```

  For more information about the api call, refer to the [Documentation](https://cloudone.trendmicro.com/docs/network-security/api-reference/tag/AWS-Connectors-API#operation/getCrossAccountListUsingGET).