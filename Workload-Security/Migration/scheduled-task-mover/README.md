# Moving your scheduled tasks from Deep Security to Cloud One Workload Security

In order to help you in the migration process from Deep Security to Cloud One Workload Security, this script will help you migrate scheduled tasks from Deep Security to Cloud One Workload Security.

## What does this script do?

This script collects your current scheduled tasks structure from Deep Security and creating the exact same structure in Cloud One Workload Security via API (this includes the tasks attached to polices, groups, computers, etc.)

## Usage

### 1. Pre-requisites:

* **Cloud One Workload Security API key**:

    - Have a [Cloud One Workload Security](https://www.trendmicro.com/en_ae/business/products/hybrid-cloud/cloud-one-workload-security.html) account. [Sign up for a free trial now](https://cloudone.trendmicro.com/register) if it's not already the case!

    - An [API key](https://cloudone.trendmicro.com/docs/account-and-user-management/c1-api-key/#create-a-new-api-key) with **"Full Access"** permission;

* **Deep Security Manager**:

    - An **Auditor** or **"READ ONLY"** [API key](https://help.deepsecurity.trendmicro.com/20_0/on-premise/api-key.html), for more details on roles, check this [link](https://help.deepsecurity.trendmicro.com/20_0/on-premise/user-roles.html);
    - Network access from the machine that you will execute the script to the Deep Security Manager;

* **Software Requirements**:

    - This script is compatible with any version of Python 3.

### 2. Deployment

- Clone this repository to the machine that you will use or download the [```mv_scheduled_tasks.py``]
- Edit the file to set the variables so the script will be able to execute API calls. These are the variables below that should set in the script:

```bash
# For Deep Security:
DSM_HOSTNAME = "<YOUR HOSTNAME HERE WITH PORT>"
DSM_API_KEY = "<YOUR DSM API KEY HERE>"

#define Cloud One Workload Security region
REGION = "<YOUR WORKLOAD REGION HERE>"
C1_API_KEY = "<YOUR C1 API KEY HERE>"
```

You're ready to execute the script! This script will notify you if there the scheduled tasks already exists and it will not create duplicates.

> **Note**: The script was tested with up to 4 levels of sub-groups, but should work just fine even with more levels.

## Contributing

If you encounter a bug or think of a useful feature or find something confusing in the docs, please [Create a New Issue](https://github.com/trendmicro/cloudone-community/issues/new)!

We :heart: pull requests. If you'd like to fix a bug or contribute to a feature or just correct a typo, please feel free to do so.

If you're thinking of adding a new feature, consider opening an [issue](https://github.com/trendmicro/cloudone-community/issues/new) first to discuss the feature to ensure it aligns with the direction of the project (and potentially
save yourself some time).

## Support

Official support from Trend Micro is not available. Individual contributors may be Trend Micro employees, but are not official support.