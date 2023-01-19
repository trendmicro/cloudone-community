# Cloud One Conformity

# Configure GCP Credentials to Conformity Bot Access

## Overview

<walkthrough-tutorial-duration duration="20"></walkthrough-tutorial-duration>

This tutorial will guide you to identify misconfigurations and address compliance to an existing GCP project by deploying Cloud One Conformity.

--------------------------------

### Permissions

The permissions that Conformity management roles will have after it has been deployed and configured are defined in:

* <walkthrough-editor-open-file filePath="cc-roles.yaml">Conformity roles</walkthrough-editor-open-file>

## Project setup

1. Select the project from the drop-down list.
2. Copy and execute the script below in the Cloud Shell to complete the project setup.

<walkthrough-project-setup></walkthrough-project-setup>

```sh
gcloud config set project <walkthrough-project-id/>
```

## Enable permissions for deployment

You need the following permissions before deployment:

### Step 1: Enable the following APIs:

* BigQuery API
* API Keys API
* Cloud Resource Manager API
* Identity and Access Management (IAM) API
* Access Approval API
* Cloud Key Management Service (KMS) API
* Compute Engine API
* Cloud Storage API
* Cloud SQL Admin API
* Cloud DNS API
* Cloud Dataproc API
* Kubernetes Engine API
* Cloud Logging API
* Cloud Pub/Sub API
* Cloud Resource Manager API


List the APIs that are enabled:

```sh
gcloud services list --enabled
```

Enable all the needed APIs at once:

```sh
gcloud services enable dns.googleapis.com bigquery.googleapis.com bigquerymigration.googleapis.com bigquerystorage.googleapis.com cloudapis.googleapis.com cloudresourcemanager.googleapis.com iam.googleapis.com accessapproval.googleapis.com cloudkms.googleapis.com compute.googleapis.com storage.googleapis.com sqladmin.googleapis.com dataproc.googleapis.com container.googleapis.com logging.googleapis.com pubsub.googleapis.com cloudresourcemanager.googleapis.com cloudasset.googleapis.com
```

--------------------------------

### Step 2: Create a custom role containing the permissions below:

* bigquery.datasets.get
* bigquery.tables.get
* apikeys.keys.list
* serviceusage.services.list
* resourcemanager.projects.get
* resourcemanager.projects.getIamPolicy
* iam.serviceAccounts.get
* accessapproval.settings.get
* cloudkms.keyRings.list
* cloudkms.cryptoKeys.list
* cloudkms.cryptoKeys.getIamPolicy
* cloudkms.locations.list
* compute.firewalls.list
* compute.networks.list
* compute.subnetworks.list
* storage.buckets.list
* storage.buckets.getIamPolicy
* compute.instances.list
* compute.images.list
* compute.images.getIamPolicy
* compute.projects.get
* cloudSql.instances.list
* compute.backendServices.list
* compute.globalForwardingRules.list
* compute.targetHttpsProxies.list
* compute.targetSslProxies.list
* compute.sslPolicies.list
* compute.urlMaps.list
* dns.managedZones.list
* dns.policies.list
* dataproc.clusters.list
* container.clusters.list
* logging.sinks.list
* logging.logMetrics.list
* monitoring.alertPolicies.list
* pubsub.topics.list
* resourcemanager.projects.get
* orgpolicy.policy.get

Naming rules:

1. **ROLE_ID length**: 3~64. ID can only include letters, numbers, periods and underscores.
1. **ROLE_TITLE length**: 1~100.

Option A: To create a custom role at the project level, execute the following command:

```sh
gcloud iam roles create CloudOneConformityAccess --project=<walkthrough-project-id/> --file=./cc-roles.yaml
```

OR

Option B: To create a custom role at the organization level, execute the following command:

```sh
gcloud iam roles create CloudOneConformityAccess --organization=<ORGANIZATION_ID> --file=../cc-roles.yaml
```

--------------------------------

### Step 3: Create the Conformity service account:

Create a custom Service Account used by Conformity Bot to get access to GCP projects and resources.

```sh
gcloud iam service-accounts create cloud-one-conformity-bot --description="GCP service account for connecting Cloud One Conformity Bot to GCP" --display-name="Cloud One Conformity Bot"
```

### Step 4: Bind the custom role to the service account:

Bind the custom role to Cloud One Conformity Service Account.

1. Get project number:

```sh
gcloud projects list --filter=<walkthrough-project-id/>
```

2. Bind service account:

```sh
gcloud projects add-iam-policy-binding <walkthrough-project-id/> \
    --member=serviceAccount:cloud-one-conformity-bot@<walkthrough-project-id/>.iam.gserviceaccount.com
    --role=projects/<walkthrough-project-id/>/roles/CloudOneConformityAccess
```

--------------------------------

For more information, see [Permissions for deployment](https://cloudone.trendmicro.com/docs/conformity/add-a-gcp-account/#set-up-access-to-conformity-gcp).

## Step 5: Generate a Service Account JSON key

# Generate a JSON file which will grant permissions for Conformity to assume the Service Account we just created:

```sh
gcloud iam service-accounts keys create Conformitykey.json --iam-account=cloud-one-conformity-bot@<walkthrough-project-id/>.iam.gserviceaccount.com
```

## Configure JSON in Conformity console

To complete the deployment process, once the key has been created, follow the steps to configure the GCP Account:

1. Go to Add Account button and select GCP Project.
2. Select the "Add new GCP Organization that new Project belongs to" option and click Next.
3. Enter a Service Account display Name. Examples: GCP Conformity.
4. Enter the value of ConformityKey.json file or download the file from CloudShell and upload to Conformity.
5. Select the GCP Projects you wish to add to Conformity and click Next.
6. Review the summary information and click Finish.

--------------------------------

## Cleanup Environment

# List Cloud One Conformity Service Accounts
gcloud iam service-accounts list --filter=cloud-one-conformity-bot

# Delete Cloud One Conformity Service Accounts
gcloud iam service-accounts delete cloud-one-conformity-bot@<walkthrough-project-id/>.iam.gserviceaccount.com

# Deletar Role
gcloud iam roles delete CloudOneConformityAccess --project=<walkthrough-project-id/>