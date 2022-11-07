[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1-inspector-findings-protection&templateURL=https://vulnerabilitytestbucket.s3.amazonaws.com/c1-inspector-findings-protection.yaml)


Amazon Inspector integration with Cloud One Workload Security

Pre-Requisites

• You must enable Amazon Inspector in your AWS account


• You need to verify the email you want to send the report (both the vulnerability report and the auto assigned report) to in Amazon SES

. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One

Background Information

Amazon Inspector is the assessment service which is for security issues and vulnerabilities to help improve the security and compliance in AWS environment. Inspector continuously scans your AWS workloads for vulnerabilities. AWS Inspector maintains a knowledge base of rules including two types of assessment, Network Based Type and Host Based Type. We are more interested in the Host Based Type which includes Common vulnerability exposures (CVEs).
Trend Micro Cloud One Workload Security IPS rules protect against Common vulnerability exposures (CVEs). Each rule has a designated CVEs that it protects against.
In this case Amazon Inspector is acting as IDS (Intrusion Detection) and Trend Micro Cloud One Workload Security IPS is acting as IPS (Intrusion Protection).
Purpose and Objective

The goal of this integration is to be able to show Trend Micro customers that are using Amazon Inspector what the Amazon findings (CVEs) are being protected by IPS rules. In order to achieve this goal, we may need to let customers understand the security risk / vulnerability issue in their environment, then we could have some opportunity to adopt a C1WS solution to mitigate / solve their issue using the ips rules.
This deployment will help customer in need or that are using Inspector to better link both cloud one Workload Security and Amazon Inspector.
The functionality of the scripts

In this project we have two deployments. The first deployment (vulnerability report) is responsible to send out a report of the vulnerabilities that are being protected by ips rules among the findings (CVEs) Inspector is detecting. The second deployment (auto assign ips rule) is responsible for assigning the ips rules found based on the Inspector findings to the computers (EC2 instances). This means if the Inspector detected any findings (CVEs) then the script will send information to Trend Micro Workload Security who will protect the instances from whatever was detected?
Deployment

• The CloudFormation Template “vulnerability_template.yaml” will send out an email which contains a csv file which is a report (the list) of the vulnerabilities (CVEs) in the client AWS account that Cloud One Workload Security ips rules are protecting against.
• The CloudFormation Template “auto-assign-ips-ruleyaml” will assign the ips rules we have in Workload Security to the appropriate instances where Amazon Inspector found the vulnerabilities (CVEs). A report of the assigned rules will be sent out (the assignment configuration) in a designated email.
Both templates can be set up to run periodically according to the releasing of ips rule weekly.
Use cron configuration to schedule the run of your lambda function. The default (cron(0/3 * ? * * *) is every 3min after the stack is completed
