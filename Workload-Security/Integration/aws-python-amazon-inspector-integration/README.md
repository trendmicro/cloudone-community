[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1-inspector-findings-protection&templateURL=https://vulnerabilitytestbucket.s3.amazonaws.com/c1-inspector-findings-protection.yaml)


Amazon Inspector integration with Cloud One Workload Security

Pre-Requisites

• You must enable Amazon Inspector in your AWS account


• You need to verify the email you want to send the report (both the vulnerability report and the auto assigned report) to in Amazon SES

. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One

. Create an s3 bucket or any bucket of your choice to upload the DeepSecurityPackageLayer zip file (DeepSecurityPackageLayer.zip)

. For more information about cron expression [Click Here](https://www.designcise.com/web/tutorial/how-to-fix-parameter-scheduleexpression-is-not-valid-serverless-error)

Background Information

Amazon Inspector is the assessment service that is used to help improve the security compliance in AWS environment. Inspector continuously scans AWS workloads looking for vulnerabilities. AWS Inspector maintains a knowledge base of rules including two types of assessment, Network Based Type and Host Based Type. We are more interested in the Host Based Type which includes Common vulnerability exposures (CVEs).
Trend Micro Cloud One Workload Security IPS rules protect against Common vulnerability exposures (CVEs). Each rule has a designated CVEs that it protects against.
In this case Amazon Inspector is acting as IDS (Intrusion Detection Service) and Trend Micro Cloud One Workload Security is acting as IPS (Intrusion Protection Service).

Purpose and Objective

The goal of this integration is to be able to show Trend Micro customers that are using Amazon Inspector which the Inspector findings (CVEs) are being protected by IPS rules. In order to achieve this goal, we may need to let customers understand the security risk / vulnerability issue in their environment, then we could have some opportunity to adopt a C1WS solution to mitigate / solve their issue using the IPS rules.
This deployment will help customer in need or that are using Inspector to better link both cloud one Workload Security and Amazon Inspector.

The functionality of the scripts

In this project we have two lambda functions The first function (vulnerability report) is responsible to send out a report of the vulnerabilities that are being protected by IPS rules among the findings (CVEs) Inspector is detecting. The second function (auto assign IPS rule) is responsible for assigning the IPS rules found based on the Inspector findings to the computers (EC2 instances). This means if the Inspector detected any findings (CVEs) then the script will send information to Trend Micro Workload Security who will protect the instances from the vulnerability detected. The "DeepSecurityPackageLayer.zip" file is used to create a Lambda layer that will be needed to run the functions. During deployment you can upload this file into the S3 bucket of your choice and reference that s3 in the yaml file (c1-inspector-findings-protection.yaml)

Deployment

The CloudFormation Template “c1-inspector-findings-protection.yaml” will deploy both lambda functions. One will send out an email which contains a csv file which is a report (the list) of the vulnerabilities (CVEs) in the client AWS account that Cloud One Workload Security IPS rules are protecting against. The other one will assign the IPS rules we have in Workload Security to the appropriate instances on which Amazon Inspector found the vulnerabilities (CVEs). A report of the assigned rules will be sent out (the assignment configuration) to a designated email.
Both functions can be set up to run periodically according to the releasing of IPS rule weekly.
Use cron configuration to schedule the run of your lambda functions. The default (cron(0 12 ? * WED *)) is every Wednesday.
