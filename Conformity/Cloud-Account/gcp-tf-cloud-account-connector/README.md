# Add GCP Account to Cloud One

 To set up a new Cloud Account, you must deploy resources in your GCP account to provide access to Trend Micro Cloud One. You can deploy the Terraform template, which will create the required GCP permissions.

## Requirements

- Have a [Cloud One](https://www.trendmicro.com/cloudone) account. [Sign up for a free trial now](https://cloudone.trendmicro.com/register) if it's not already the case!
- GCP CLI [installed](https://cloud.google.com/sdk/docs/install) and [configured](https://cloud.google.com/sdk/docs/initializing).
- Enable the following Google APIs:

|Service|APIs & Services|
|---|---|
|BigQuery|BigQuery API|
|CloudAPI|API Keys API|
|CloudIAM|Cloud Resource Manager API<br>Identity and Access Management (IAM)<br>API Access Approval API|
|CloudKMS|Cloud Key Management Service (KMS) API|
|CloudVPC|Compute Engine API|
|CloudStorage|Cloud Storage API|
|ComputeEngine|Compute Engine API|
|CloudSQL|Cloud SQL Admin API|
|CloudLoadBalancing|Compute Engine API|
|CloudDNS|Cloud DNS API|
|Dataproc|Cloud Dataproc API|
|GKE|Kubernetes Engine API|
|CloudLogging|Cloud Logging API|
|PubSub|Cloud Pub/Sub API|
|ResourceManager|Cloud Resource Manager API|

## Setup IAM Permissions

To setup the IAM permission I've create a terraform template that you can use, it will create the policy, role and the attachment between them, first clone the repository to your machine and access the folder of this project, here the commands to deploy the permissions via terraform:

 To install terraform, follow this [Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli#install-terraform)

 First you need to provide in the terraform template (variables.tf file) or use the example `gcp.tfvars` file, these are the values that need to be provided:

- Project ID
- GCP Region

Then you can execute the following:

   ```bash
   cd IAM
   terraform init
   terraform plan -out=plan
   terraform apply -auto-approve (In case you are replacing the values directly on the `variables.tf`)
   terraform apply -var-file="gcp.tfvars` (In case you decided to use the `gcp.tfvars`)
   ```

After finish execution, a file called `gcp-key.json` will be at the local path, this file must be used in the conformity UI or API to finish the account onboarding.