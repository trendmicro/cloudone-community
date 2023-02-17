# Cloud One Connector Automation

 This automation is intended to streamline the process of setting up the Cloud One common connector for AWS, workload security connector for AWS and the AWS cloudtrail integration.

## Requirements

- Have a [Cloud One](https://www.trendmicro.com/cloudone) account. [Sign up for a free trial now](https://cloudone.trendmicro.com/register) if it's not already the case!
- Have a  Vision One account.
- [Register Vision One into Cloud One](https://cloudone.trendmicro.com/docs/integrations/xdr/#register-with-trend-micro-vision-one-xdr)
- AWS CLI [installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
- Terraform CLI (To install terraform, follow this [Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli#install-terraform))

After cloning this repo, go to the `connectors.tfvars` and input the required information to deploy the connectors to Cloud One.

 Then you can execute the following:

   ```
   terraform init
   terraform plan -var-file="connectors.tfvars"
   terraform apply -auto-approve -var-file="connectors.tfvars"
   ```

All the connectors should be deployed, to check the status on the cloudtrail integration, go to the cloudformation page in the desired AWS account to check the status, once completed, you should be able to receive the events on your Vision One account.

If at any point you decided to remove the connectors, simply execute:

   ```
   terraform destroy -auto-approve -var-file="connectors.tfvars"
   ```

All the connectors will be removed once finished, the cloudtrail integration might take longer to finish the destroying process.
