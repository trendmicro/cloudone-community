
# Deploy the All-In-One stack with Plugin Promote and Quarantine.
This script will deploy the File Storage Security AIO Stack with the promote/quarantine lambda functionality as a nested stack. 

Launch the CloudFormation template provided below.
[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=c1-fss-aio-v2&templateURL=https://aws-workshop-c1as-cft-templates.s3.amazonaws.com/aws-aio-nested-w-plugin.yaml)


## Prerequisites

1. **Create S3 buckets**
    - Create a 'Scanning bucket' to be monitored by File Storage Security.
    - Create a 'Promote bucket' to receive clean files. Example: `fss-promote`.
    - Create a 'Quarantine bucket' to receive quarantined files. Example: `fss-quarantine`.

## Stack Parameters

Fill out the Quick create stack page as follows:

- Stack name: Specify the name of the stack. Example: FileStorageSecurity-All-In-One.
- S3BucketToScan: Specify the name of your S3 bucket to scan, as it appears in S3. You can only specify one bucket.
- ScannerEphemeralStorage: The size of the scanner lambda function's temp directory in MB. The default value is 512, but it can be any whole number between 512 and 2048 MB. Configure a large ephemeral storage to scan larger files in zip files.
- PROMOTEBUCKET: 'Promote bucket' to receive clean files.
- QUARANTINEBUCKET: 'Quarantine bucket' to receive quarantined files.
- Trend Micro Cloud One region: Cloud One account region
- ExternalID: Cloud One Account Ext ID.
  


## Test the Application

To test that the application was deployed properly, you'll need to generate a malware detection using the [eicar test file](https://secure.eicar.org/eicar.com "A file used for testing anti-malware scanners."), and then check the Quarantine bucket to make sure the `eicar` file was sent there successfully.

1. **Download the Eicar test file**
   - Temporarily disable your virus scanner or create an exception, otherwise it will catch the `eicar` file and delete it.
   - Browser: Go to the [eicar file](https://secure.eicar.org/eicar.com) page and download `eicar_com.zip` or any of the other versions of this file.
   - CLI: `curl -O https://secure.eicar.org/eicar_com.zip`
2. **Upload the eicar file to the ScanningBucket**

    - Using the AWS console

        1. Go to **CloudFormation > Stacks** > your all-in-one stack > your nested storage stack.
        2. In the main pane, click the **Outputs** tab and then copy the **ScanningBucket** string. Search the string in Amazon S3 console to find your ScanningBucket.
        3. Click **Upload** and upload `eicar_com.zip`. File Storage Security scans the file and detects malware.
        4. Still in S3, go to your Quarantine bucket and make sure that `eicar.zip` file is present.
        5. Go back to your ScanningBucket and make sure the `eicar.zip` is no longer there.

        > 📌 It can take 15-30 seconds or more for the 'move' operation to complete, and during this time, you may see the file in both buckets.

    - Using the AWS CLI

        - Enter the folowing AWS CLI command to upload the Eicar test file to the scanning bucket:
            `aws s3 cp eicar_com.zip s3://<YOUR_SCANNING_BUCKET>`
        - where:
            - `<YOUR_SCANNING_BUCKET>` is replaced with the ScanningBucket name.

        > **NOTE:** It can take about 15-30 seconds or more for the file to move.