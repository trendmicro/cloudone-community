# Subscribe deployed FSS Storage Stack SNS topics to Slack Notification Plugin.
This script will subscribe a deployed Slack plugin to all FSS storage stacks. After deployment any malicious event will be sent to the defined slack channel. 

**Before you deploy**

   * Install supporting tools
        - Install and configure the AWS command line interface (CLI). 
        See [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) for details.

   * If not already present, [deploy the Slack Plugin for File Storage Security](https://github.com/trendmicro/cloudone-filestorage-plugins/tree/master/post-scan-actions/aws-python-slack-notification).
  
  * Obtain the following parameters.
      - **API Key** - Generate a [Cloud One API Key](https://cloudone.trendmicro.com/docs/account-and-user-management/c1-api-key/)
      - **Cloud One Account** [**Region**](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-regions/) - example: ```us-1```.
      - **Name** of the Slack Lambda Function.
      - **ARN** of the Slack Lambda Function.

<hr>

**1. Clone Repo**
 - Clone this repository
 - After cloning repo:
 ```
   cd .\cloudone-community\File-Storage-Security\Post-Scan-Action-Automations\aws-slack-notification-automation
```

**2. Run Script**
   - Open terminal/cmd:
   ```
      .\auto-slack.py --apikey <apikey here> --c1region <c1 account region> --functionname <name of slack function --functionarn <slack function arn> --awsprofile <> --awsregion <aws region to operate in>
   ```  

