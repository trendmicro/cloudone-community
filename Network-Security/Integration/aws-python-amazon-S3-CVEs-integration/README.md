# Cloud One Network Security policy update based on CVEs injested in S3 bucket.

This script will deploy a lambda function that will auto update Cloud One Network Security policy  whenever a csv file (that contains [CVEs](https://www.cve.org/About/Overview)) gets uploaded in a designated S3 bucket. 

Click the below to launch the CloudFormation template.

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1ns-CVEs-Integration-template&templateURL=https://cloudone-community.s3.amazonaws.com/c1ns-policy-update-s3-cve-template.yaml)


## Prerequisites

1. Valid [Cloud One account](https://cloudone.trendmicro.com/trial) with current subscription to [Network Security](https://aws.amazon.com/marketplace/pp/prodview-g232pyu6l55l4).

2. You need [to verify the email](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html) you want to send the report (both the Intrusion Prevention Filtering report and the updated policy report) to in Amazon SES

3. Generate the [API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) from Cloud One

4. Have an existing S3 bucket where the CVEs are uploaded or create new S3 bucket. In case you do not have any existing bucket the template will create a new bucket for you.
    > **NOTE:** Make sure the existing bucket does not have Event notification attached to other lambda function.
                Make sure the new bucket has a unique name.
