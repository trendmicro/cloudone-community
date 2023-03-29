# Cloud One Network Security policy update based on HIGHLY-EXPLOITABLE UNIQUE CVEs from Vision One.

This script will deploy a lambda function that will auto update Cloud One Network Security policy based on Vision One VULNERABILITY MANAGEMENT METRICS (that contains [CVEs](https://www.cve.org/About/Overview)). 

Click the below to launch the CloudFormation template.


[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1ns-v1-vulnerability-protection&templateURL=https://cloudone-community.s3.us-east-1.amazonaws.com/latest/Network-Security/Integration/aws-python-amazon-CVEs-from-V1/templates/c1ns-policy-update-v1-cve-template.yaml)


## Prerequisites

1. Valid [Cloud One account](https://cloudone.trendmicro.com/trial) with current subscription to [Network Security](https://aws.amazon.com/marketplace/pp/prodview-g232pyu6l55l4).

2. You need [to verify the email](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html) you want to send the report (the updated policy report) to, in Amazon SES.

3. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One.

4. Valid [Vision One account](https://aws.amazon.com/marketplace/pp/prodview-skoruk3n7ag5w?sr=0-1&ref_=beagle&applicationId=AWSMPContessa) or [Free trial](https://cloudone.trendmicro.com/trial?_ga=2.66851502.1835612034.1680036408-646949698.1678486785&_gac=1.15653188.1680126647.Cj0KCQjww4-hBhCtARIsAC9gR3aS0iyBcz1T11_7DWmA4JmfDaFg4UgwTS2MxtQvBw2RPB3rUDYMNz4aAlvREALw_wcB).

5. Have a [Network Security](https://cloudone.trendmicro.com/docs/network-security/Network_Security_for_AWS/) deployed.

6. Generate the [Vision One Token](https://docs.trendmicro.com/en-us/enterprise/trend-micro-xdr-help/ObtainingAPIKeys) from Vision One console.



## Purpose and Objective

The goal of this integration is to be able to automate the update of the appropriate intrusion prevention  filters in the policy to (mitigate the HIGHLY-EXPLOITABLE UNIQUE CVEs from Vision One) enforced this protection.

## Deployment

The CloudFormation Template ```c1ns-policy-update-v1-cve-template.yaml``` will deploy a lambda function. The function will send out an email which contains a csv file with a report (the list) of the intrusion prevention filterings updated in Network Security Policy based on the vulnerabilities ([CVEs](https://www.cve.org/About/Overview)) from Vision One.
The function is set up to run periodically (Weekly).
Use cron configuration to schedule the run of your lambda function. The default {cron(0 12 ? * WED *)} is every Wednesday.

## Stack Parameters

Fill out the followings when creating your stack:

- **Stack name**: Specify the name of the stack. The default is ```c1ns-v1-vulnerability-protection``` when using quick start deployment.

- **Sender Email**: The email that is registered in Amazon SES to send out notification.

- **Reciever Email**: The email where the reports need to be send to.

- **Action Set**: the recommended ActionSet you would like apply to the Intrusion Prevention Filtering.

- **Cloud One Region**: Your Cloud One Region.

- **Cron Schedule**: This will help define the period you will like your lambda functions to be running, the default is every Wednesday. 

- **Token**: Your Vision One Authentication Token.

- **ApiKey**: Your Cloud One Api Key.