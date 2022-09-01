# Enable CloudWatch Visibility for Networks Security Managed Endpoint.

### Prerequisites to stack deployment.

1. Your AWS Account has been added to Cloud One Network Security. See our documentation to [add your AWS Cloud Account](https://cloudone.trendmicro.com/docs/network-security/add_cloud_accounts_appliances/#add-cloud-accounts-and-appliances).

2. Ensure you have a deployed the Trend Micro Network Security managed service, if not see [here](https://cloudone.trendmicro.com/docs/network-security/NSMS_deploy_overview/). 

3. Ensure the Endpoint deployment is [valid](https://cloudone.trendmicro.com/docs/network-security/NSMS_validate_deployment/)

4. Once the Network Security Endpoint stack is deployed.
- In CloudFormation, locate the NS connector stack deployed previously to add your Cloud One Account: ```C1NS-Cloud-Account-Management```. 
- Select the **Parameters** tab.
- Copy down the **ExternalID** value.
- Obtain your **AWS Account ID** by clicking your name/user in the top right. Copy this value down.

5. Copy down the **VPC-ID** of the VPC you deployed the NS endpoint in.

---

### Specify stack details.
- **StackName** - Define a name for your Cloudformation stack.
- **C1NSRegion** - The AWS region where the NS VPC endpoint resides. 
- **DashboardName** - Define a name for your CloudWath Panel.
- **LogStream** - use the below following format below, replacing the values appropriately.

```NSaaS-<External ID here>-<AWS Account ID Here>-<VPC-ID here>```

Example: ```NSaaS-340002837676-013257365352-vpc-00ff298e7578fb3a9```

- Review the stack details and click on **Create Stack**.