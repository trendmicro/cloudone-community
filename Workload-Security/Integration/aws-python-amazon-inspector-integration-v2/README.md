# Cloud One Workload Security Integration with Amazon Inspector.

This script will deploy two lambda functions, one will run (on a schedule based, the default is every wednesday)a report of vulnerabilities from EC2 instances that Amazon Inspector detects and match them against Trend Micro IPS rules. The second Lambda function will assign thoses rules or virtual patches to protect workloads against [CVE](https://www.cve.org/About/Overview)’s automattically as soon as Amazon Inspector detects them. 
    > **Key:** In this case Amazon Inspector as vulnerability scanner and Trend Micro Cloud One Workload Security is acting as IPS (Intrusion Protection Service).

Click the below to launch the CloudFormation template.

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1ws-inspector-findings-protectionV2&templateURL=https://cloudone-community.s3.us-east-1.amazonaws.com/latest/Workload-Security/Integration/aws-python-amazon-inspector-integration-v2/templates/c1ws-inspector-findings-template.yaml) 


## Prerequisites

1. Valid [Cloud One account](https://cloudone.trendmicro.com/trial) with current subscription to [Workload Security](https://aws.amazon.com/marketplace/pp/prodview-g232pyu6l55l4).

2. You must enable [Amazon Inspector](https://docs.aws.amazon.com/inspector/latest/user/getting_started_tutorial.html) in your AWS account.

3. You need to accept the invitation send to your email to subscribe to the sns notification.

4. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One.

5. Create an s3 bucket (Optional) or use an existing s3 bucket of your choice to received the reports in csv file


6. For more information about cron expression [Click Here](https://www.designcise.com/web/tutorial/how-to-fix-parameter-scheduleexpression-is-not-valid-serverless-error)

 

 ## Deployment

The CloudFormation Template “c1ws-inspector-findings-template.yaml” will deploy both lambda functions. One will send out notification about the rules that was assign. The second will send out notification about the CVEs and instances that can be protected using Cloud One Workload Security IPS rules. The first runs everytime there is new CVE from Amazon Inspector.
The second function is set to run periodically according to the releasing of IPS rule weekly.
Use cron configuration to schedule the run of your lambda functions. The default (cron(0 12 ? * WED *)) is every Wednesday.

> **NOTE:** 
    This deployment is applicatble to AWS Organization/Control Tower account.
