[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1ns-inspector-findings-protection&templateURL=https://vulnerabilitytestbucket.s3.amazonaws.com/c1ns-inspector-findings-template.yaml)


Amazon Inspector integration with Cloud One Network Security

Pre-Requisites

• You must enable Amazon Inspector in your AWS account


• You need to verify the email you want to send the report (both the Intrusion Prevention Filtering report and the updated policy report) to in Amazon SES

. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One


. For more information about cron expression [Click Here](https://www.designcise.com/web/tutorial/how-to-fix-parameter-scheduleexpression-is-not-valid-serverless-error)

Background Information

Amazon Inspector is the assessment service that is used to help improve the security compliance in AWS environment. Inspector continuously scans AWS workloads looking for vulnerabilities. AWS Inspector maintains a knowledge base of rules including two types of assessment, Network Based Type and Host Based Type. We are more interested in the Host Based Type which includes Common vulnerability exposures (CVEs).
Trend Micro Cloud One Network Security protects against Common vulnerability exposures (CVEs). Network Security has a policy that contains more than 23000 Intrusion Prevention Filterings. These filters help protect against CVEs.
In this case Amazon Inspector is acting as IDS (Intrusion Detection Service) and Trend Micro Cloud One Network Security is acting as IPS (Intrusion Protection Service).

Purpose and Objective

The goal of this integration is to be able to show the CVEs (findings in Amazon Inspector) that Network Security can protect and make sure we have the appropriate filters updated in the policy to (mitigate the Inspector Findings) enforced this protection.

The functionality of the scripts

In this project we have two lambda functions the first function (FindingsReportLambda) is responsible to send out a report of the vulnerabilities (CVEs) that are being protected by Network Security Policy in comparison to the Amazon Inspector findings (CVEs). The second function (PolicyUpdateLambda) is responsible for updating the Network Security policy in order protect against the inspector findings. This means if the Inspector detected any findings (CVEs) then the script will send information to Trend Micro Network Security who will protect against the vulnerabilities detected.

Deployment

The CloudFormation Template “c1ns-inspector-findings-template.yaml” will deploy both lambda functions. One will send out an email which contains a csv file which is a report (the list) of the vulnerabilities (CVEs) in the AWS account that Cloud One Network Security is protecting against. The other one will update the policy. A report of the updated policy containing the Intrusion Prevention Filtering will be sent out (the assignment configuration) to a designated email.
Both functions can be set up to run periodically.
Use cron configuration to schedule the run of your lambda functions. The default {cron(0 12 ? * WED *)} is every Wednesday.