# Sync Well-Architected Review

This tool uses Cloud One Conformity to update your workload review with a summary of relevant check data in the "Notes" section of each review question. For an explanation of the fields in this summary, see [Understanding the Check Summary Report](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Well-Architected-Tool#understanding-the-check-summary-report). This automation is provided by the [Conformity API](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Well-Architected-Tool) which will receive a request and add all the notes to the chosen Well-Architected Review workload.

To know more about the Well-Architect Review, check this [Blog Post](https://newsroom.trendmicro.com/2020-12-16-Companies-Leveraging-AWS-Well-Architected-Reviews-Now-Benefit-from-Security-Innovations-from-Trend-Micro)


## Requirements

- Have a [Cloud One](https://www.trendmicro.com/cloudone) account. [Sign up for a free trial now](https://cloudone.trendmicro.com/register) if it's not already the case!
- An [API key](https://cloudone.trendmicro.com/docs/account-and-user-management/c1-api-key/#create-a-new-api-key) with **"Full Access"** permission;
- This API is only available to ADMIN users.
- AWS CLI [installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
- An active Conformity AWS Account ID in your organization
- Your Conformity Organization's external ID.
- The ARN of a defined Well-Architected workload, to retrieve the workload arn you can use the following AWS CLI command:

    ```bash
    aws wellarchitected list-workloads
    ``` 
    
    ## Setup IAM Permissions

    To setup the IAM permission I've created a terraform template that you can use, it will create the policy, role and the attachment between them, first clone the repository to your machine and access the folder of this project, here the commands to deploy the permissions via terraform:

    To install terraform, follow this [Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli#install-terraform)

    First you need to provide in the terraform template (variables.tf file):
    - Cloud One API Key with `full-access` permissions
    - Cloud One Region
    - Well-Architected Workload
    - AWS Region

    Then you can execute the following:

    ```
    cd IAM
    terraform init
    terraform plan -out=plan
    terraform apply -auto-approve
    ```

    At the end, the arn of the role will be printed in the output, keep this value to use it in the sync api call.

    In case you rather to create via AWS console or CLI, check this documentation where we describe the step-by-step instructions: https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Well-Architected-Tool#set-up-iam-role-via-aws-cli
    
    ## Syncing with the Well-Architected Review

    To make the api call to sync, you will need first to retrieve the `account id` from the conformity api additionally. Here is an example on how to make this api call:

    ```bash
    curl -k -s -X GET https://conformity.{region}.cloudone.trendmicro.com/api/accounts \
        -H "Authorization: ApiKey <YOUR-CLOUDONE-API-KEY>" \
        -H 'api-version: v1' \
        -H "Content-Type: application/vnd.api+json"
    ```
    Collect the id of the account that you want to sync, for more details in the api call, please refer to [How to list Conformity accounts](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Accounts#paths/~1accounts/get).

    To make the api call to sync, here is how you can do it:


    ```bash
    curl -k -s -X POST https://conformity.{region}.cloudone.trendmicro.com/api/well-architected-tool/sync \
        -H "Authorization: ApiKey <YOUR-CLOUDONE-API-KEY>" \
        -H 'api-version: v1' \
        -H "Content-Type: application/vnd.api+json" \
        -d '{ "meta": { "accountId": "84371h26-9839-12u5-a017-7936837b2d9b", "roleArn": "arn:aws:iam::93469203752:role/well-architected-tool-role", "workloadArn":"arn:aws:wellarchitected:us-east-1:38920491820:workload/60d5038912d5b548dfdfwer2354f" } }' | jq
    ```

    You should see a message like this:

    ```json
    { "meta": { "status": "In Progress", "requestId": "67392ee6-620f-4c1d-b262-0b91bbc3b562", "message": "Syncing Well-Architected review for workload 0f9dd75e28124cc82387uxbs2c1d3e9s in background" } }
    ```

    To view the updates made to the review, navigate to `Well-Architected Tool > Workloads > {YOUR_WORKLOAD_NAME} > AWS Well-Architected Framework` and select any question in the review. In a couple of minutes you should be able to see the notes being added to your Well-Architected Review, similar to this:

    ```
    Here are your findings from Trend Micro Cloud One Conformity:
    Total number of Successes: 444
    Total number of Failures: 212
    By risk level
    -  Extreme successes: 1, failures: 0
    -  Very High successes: 0, failures: 0
    -  High successes: 135, failures: 16
    -  Medium successes: 307, failures: 175
    -  Low successes: 1, failures: 21
    Rule Ids to Review: [RTM-002, IAM-052, IAM-045, CWL-014, IAM-034, IAM-035, IAM-042, RTM-001, IAM-061, CC-002, IAM-014, IAM-015, IAM-030, IAM-036, IAM-048, CFM-001, CFM-002, CFM-005, IAM-057, CFM-004, Lambda-005, CFM-006, AG-007, CF-004, CWL-017, IAM-058, WAF-001, Lambda-002, IAM-050, Organizations-002, WellArchitected-001, S3-013, CFM-003]
    ```

    ## Troubleshooting

    For any errors, please follow the [Documentation](https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Well-Architected-Tool)