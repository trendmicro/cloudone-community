# Cloud One Conformity

# Configure GCP Organization and Projects to Cloud One Conformity

## Overview

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

This tutorial will guide you to the set up configuration of your GCP organization and projects to Cloud One Conformity.
The Conformity deployment script will create:

* Cloud One Conformity Bot Service Account on your Security Project
* A custom role will be created at Organization level
* Map the Conformity Bot Service Account to all projects
* Add all GCP projects to Cloud One Conformity console

--------------------------------

### Permissions

The permissions that Conformity management roles will have after it has been deployed and configured are defined in:

* <walkthrough-editor-open-file filePath="cc-roles.yaml">Conformity roles</walkthrough-editor-open-file>

## Security Project Setup

1. Select the project from the drop-down list as your Security Project.
2. Copy and execute the script below in the Cloud Shell to complete the project setup.

<walkthrough-project-setup></walkthrough-project-setup>

```sh
gcloud config set project <walkthrough-project-id/>
```

## Enable permissions for deployment

You need the following in order to deploy Cloud One Conformity (Don't worry, the deployment script will enable them all):

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
* Cloud Assets API

--------------------------------

### Step 2:Configure and deploy Conformity deployment script:

1. **GCP Organization Name:** Specify the Name of the GCP organisation in Cloud One Conformity console.
2. **Cloud One API Key:** The [Cloud One API Key](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-api-key/) used to add GCP Projects into Cloud One Conformity management console.
3. **Cloud One region:** Specify the region ID of your Trend Micro Cloud One account. For the list of supported Cloud One regions, see [Trend Micro Cloud One regions](https://cloudone.trendmicro.com/docs/identity-and-account-management/c1-regions/). The default region is `us-1`.

```sh
./deployment-script.sh -d <GCP_Organization_Name> -o <CLOUD_ONE_APY_KEY> -c <CLOUD_ONE_REGION>
```

### Step 3:Review Conformity checks:

Now all projects has been added to the console, review the misconfigurations by pillar, resource or frameworks/standards to increase your security posture on the public cloud.
Utilize our [knowledge base](https://www.trendmicro.com/cloudoneconformity/knowledge-base/gcp/) and set up the [communication channels](https://cloudone.trendmicro.com/docs/conformity/communication-channels/) to address the findings with our team and workflow.

--------------------------------

### Cleanup

To remove the Conformity Bot Service Account from projects and delete it from your security project, you can run our cleanup script. This script will not remove the projects from Cloud One Conformity console.
* <walkthrough-editor-open-file filePath="remove-script.sh">Cleanup Script</walkthrough-editor-open-file>

```sh
./remove-script.sh 
```
