# Deploy to All Existing S3 Resource
This script will deploy File Storage Security Stack to all buckets unless defined in exclusions text file. After deployment the stack will be registered with Cloud One Console. 

**Before you deploy**

   * If not already present, [deploy a Scanner Stack](https://cloudone.trendmicro.com/docs/file-storage-security/stack-add-aws/) in the Cloud One - File Storage Security account.
  * Obtain the Scanner Stack LambdaAlias ARN Value and SQS URL
      - Go to AWS Console > Services > CloudFormation
      - Click on the **Name of your Scanner Stack**
         - Select the **OutPuts Tab**
         - Copy the name of your **Scanner Stack** 
         - Copy the value of **ScannerLambdaAliasARN** 
         - Copy the value of the **ScannerQueueURL**
   
   * **Obtain the AWS Account ID value in the AWS Account the Scanner Stack was deployed.**
   
   * Obtain your Cloud One API Key
      - Generate API Key: [Cloud One API Key](https://cloudone.trendmicro.com/docs/account-and-user-management/c1-api-key/)
   * Obtain your Cloud One Region
      - Sign in to your Cloud One console > Administration > Account Settings
      -  Copy the value of the **Region**.

<hr>

**1. Clone Repo**
 - Clone this repository
 - After cloning repo:
 ```
   cd .\cloudone-community\File-Storage-Security\deployment\python-deploy-to-all-existing-s3\
```

**2. Create the Exclusions text file**
   * Create a new file called `exclude.txt` with names of S3 buckets to exclude from FSS deployment or run the command below to list buckets and write them all to a file called exclude.txt
      - If you run the command below to create the exclusions file then you must remove the bucket names that you File Storage Security to be deployed on.
   - 1 per line, Example: [exclude.txt](https://github.com/trendmicro/cloudone-community/blob/main/File-Storage-Security/Deployment/python-deploy-to-all-existing/exclude.txt)
   * For organizations with a large number of buckets, a list of S3 buckets can be piped into exclude.txt using the aws cli and PowerShell:

   
  
   [Mac/Linux]
   ```
    aws s3 ls | awk '{print$3}' > exclude.txt
   ```
   [Windows]
   ```
   #install awk with chocolatey
    aws s3 ls | awk '{print$3}' > exclude.txt
   ```

**3. Run Script**
   - Open terminal/cmd:
   
   [Windows]
   ```
      .\deploy.py --account <AWS Account ID where scanner stack exists> --c1region <cloud one region; example: us-1> --scanner <Scanner Stack Name> --scanneralias <Scanner LambdaAlias ARN value> --sqs <Scanner Stack SQS URL> --apikey <CloudOne-API-Key>
   ```  
   
   [Mac/Linux]
   ```
     python3 deploy.py --account <AWS Account ID where scanner stack exists> --c1region <cloud one region; example: us-1> --scanner <Scanner Stack Name> --scanneralias <Scanner LambdaAlias ARN value> --sqs <Scanner Stack SQS URL> --apikey <CloudOne-API-Key>
   ```


# Additional Notes

### S3:ObjectCreated:* event in use
S3 buckets with existing event notification will be skipped for FSS deployment. Please see the Cloud One documentation [here](https://cloudone.trendmicro.com/docs/file-storage-security/aws-object-created-event-in-use/) for further deployment details.

### Tags

The Script will choose whether or not to deploy a storage stack depending on a bucket's tags. **See below for details**:

| Tag            | Value  | Behavior                       |
| -------------- | ------ | ------------------------------ |
| [no tag]       | [none] | Storage Stack deployed         |
| `FSSMonitored` | `yes`  | Stack Already Exists(skip)     |
| `FSSMonitored` | `no`   | Storage Stack **NOT** deployed |

### Supported FSS regions

Please note this script supports only S3 buckets deployed in [AWS Regions File Storage Security Supports](https://cloudone.trendmicro.com/docs/file-storage-security/supported-aws/#AWSRegion). Buckets deployed in unsupported FSS AWS regions need to be excluded from deployemnts.
