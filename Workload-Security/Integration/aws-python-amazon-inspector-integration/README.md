# Cloud One Workload Security Integration with Amazon Inspector.

This script will deploy two lambda functions, one will run a report of vulnerabilities from EC2 instances that Amazon Inspector detects and match them against Trend Micro IPS rules. The second Lambda function will assign thoses rules or virtual patches to protect workloads against [CVE](https://www.cve.org/About/Overview)’s automattically as Amazon Inspector detects them. 
    > **Key:** In this case Amazon Inspector as vulnerability scanner and Trend Micro Cloud One Workload Security is acting as IPS (Intrusion Protection Service).

Click the below to launch the CloudFormation template.

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1ws-inspector-findings-protection&templateURL=https://cloudone-community.s3.us-east-1.amazonaws.com/latest/Workload-Security/Integration/aws-python-amazon-inspector-integration/templates/c1ws-inspector-findings-template.yaml) 



## Prerequisites

1. Valid [Cloud One account](https://cloudone.trendmicro.com/trial) with current subscription to [Workload Security](https://aws.amazon.com/marketplace/pp/prodview-g232pyu6l55l4).

2. You must enable [Amazon Inspector](https://docs.aws.amazon.com/inspector/latest/user/getting_started_tutorial.html) in your AWS account.

3. You need to [verify the email](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html) you want to send the report (both the vulnerability report and the auto assigned report) to, in Amazon SES.

4. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One.

5. Create an s3 bucket or use an existing s3 bucket of your choice to upload the DeepSecurityPackageLayer zip file (DeepSecurityPackageLayer.zip)

   > **NOTE:**  The "DeepSecurityPackageLayer.zip" file is used to create a Lambda layer that will be needed to run the functions. During deployment you can upload this file into the S3 bucket of your choice and reference that s3 bucket in the yaml file (c1-inspector-findings-protection.yaml).

6. For more information about cron expression [Click Here](https://www.designcise.com/web/tutorial/how-to-fix-parameter-scheduleexpression-is-not-valid-serverless-error)

 

 ## Deployment

The CloudFormation Template “c1ws-inspector-findings-template.yaml” will deploy both lambda functions. One will send out an email which contains a csv file which is a report (the list) of the vulnerabilities (CVEs) in the client AWS account that Cloud One Workload Security IPS rules are protecting against. The other one will assign the IPS rules we have in Workload Security to the appropriate instances on which Amazon Inspector found the vulnerabilities (CVEs). A report of the assigned rules will be sent out (the assignment configuration) to a designated email.
Both functions can be set up to run periodically according to the releasing of IPS rule weekly.
Use cron configuration to schedule the run of your lambda functions. The default (cron(0 12 ? * WED *)) is every Wednesday.
