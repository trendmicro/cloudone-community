
# Amazon Inspector integration with Cloud One Network Security 

This script will deploy a lambda functions that facilitate the integration. 

Click the below to launch the CloudFormation template.

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1ns-inspector-findings-protection&templateURL=https://cloudone-community.s3.amazonaws.com/latest/Network-Security/Integration/aws-python-amazon-inspector-integration/c1ns-inspector-findings-template.yaml)


Pre-Requisites

1. You must enable [Amazon Inspector](https://docs.aws.amazon.com/inspector/latest/user/getting_started_tutorial.html) in your AWS account 


2. You need [to verify the email](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html) you to send the reports to (both the Intrusion Prevention Filtering report and the updated policy report) in Amazon SES

3. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One


4. For more information about cron expression [Click Here](https://www.designcise.com/web/tutorial/how-to-fix-parameter-scheduleexpression-is-not-valid-serverless-error)


## Purpose and Objective

The goal of this integration is to be able to show the CVEs (findings in Amazon Inspector) that Network Security can protect and make sure we have the appropriate filters updated in the policy to (mitigate the Inspector Findings) enforced this protection.

## Deployment

The CloudFormation Template ```c1ns-inspector-findings-template.yaml``` will deploy both lambda functions. One will send out an email which contains a csv file which is a report (the list) of the vulnerabilities ([CVEs](https://www.cve.org/About/Overview)) in the AWS account that Cloud One Network Security is protecting against. The other one will update the policy. A report of the updated policy containing the Intrusion Prevention Filtering will be sent out (the assignment configuration) to a designated email.
Both functions can be set up to run periodically.
Use cron configuration to schedule the run of your lambda functions. The default {cron(0 12 ? * WED *)} is every Wednesday.

## Stack Parameters

Fill out the followings when creating your stack:

- **Stack name**: Specify the name of the stack. The default is ```c1ns-inspector-findings-protection ```

- **Sender Email**: The email that is registered in Amazon SES to send out notification.

- **Reciever Email**: The email where the reports need to be send to.

- **Action Set**: the recommended ActionSet you would like apply to the Intrusion Prevention Filtering.

- **Cloud One Region**: Your Cloud One Region.

- **Cron Schedule**: This will help define the period you will like your lambda functions to be running, the default is every Wednesday. 