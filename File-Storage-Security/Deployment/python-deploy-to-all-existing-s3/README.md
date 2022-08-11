# Deploy to All Existing S3 Resource
This script will deploy File Storage Security Stack to all buckets unless defined in exclusions text file. After deployment the stack will be registered with Cloud One Console. 

**Before you deploy**

   * If not already present, [deploy a Scanner Stack](https://cloudone.trendmicro.com/docs/file-storage-security/stack-add-aws/) in the Cloud One - File Storage Security account.
  * Obtain the Scanner Stack Name and SQS URL
      - Go to AWS Console > Services > CloudFormation
      - Click **Name of Scanner Stack**
         - Copy **Stack Name** 
      - Under **Outputs** tab
         - Copy **ScannerQueueURL**
      - StackName: `Enter name for stack`
   * Obtain your Cloud One API Key
      - Generate API Key: [Cloud One API Key](https://cloudone.trendmicro.com/docs/account-and-user-management/c1-api-key/)

<hr>

**1. Clone Repo**
 - Clone this repository
 - After cloning repo:
 ```
   cd .\cloudone-community\File-Storage-Security\deployment\python-deploy-to-all-existing-s3\
```

**2. Create the Exclusions text file**
   * Create a new file called `exclude.txt` with names of S3 buckets to exclude from FSS deployment.
   - 1 per line, Example: [exclude.txt](https://github.com/trendmicro/cloudone-community/blob/main/File-Storage-Security/Deployment/python-deploy-to-all-existing/exclude.txt)
   * For organizations with a large number of buckets, a list of S3 buckets can be piped into exclude.txt using the aws cli and PowerShell:
   ```
    aws s3 ls | Out-File -FilePath C:\<FILEPATH>\exclude.txt ; C:\<FILEPATH-AGAIN>\exclude.txt
   ```
**3. Run Script**
   - Open terminal/cmd:
   ```
      .\deploy.py --account <aws account id> --c1region <cloud one region; example: us-1> --scanner <Scanner Stack Name> --sqs <SQS URL> --apikey <CloudOne-API-Key>
   ```  


# Additional Notes

### Tags

The Script will choose whether or not to deploy a storage stack depending on a bucket's tags. **See below for details**:

| Tag            | Value  | Behavior                       |
| -------------- | ------ | ------------------------------ |
| [no tag]       | [none] | Storage Stack deployed         |
| `FSSMonitored` | `yes`  | Stack Already Exists(skip)     |
| `FSSMonitored` | `no`   | Storage Stack **NOT** deployed |

### Supported FSS regions

Please note this script supports only S3 buckets deployed in [AWS Regions File Storage Security Supports](https://cloudone.trendmicro.com/docs/file-storage-security/supported-aws/#AWSRegion). Buckets deployed in unsupported FSS AWS regions need to be excluded from deployemnts.
