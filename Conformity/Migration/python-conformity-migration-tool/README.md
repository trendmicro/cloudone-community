# conformity-migration-tool
Migrates your visiblity information in cloudconformity.com to cloudone.trendmicro.com

## **⚠ WARNING: This tool will overwrite your Cloud One Conformity**

## Requirements
1. Python v3.7+
2. Both accounts must have a valid license (Not expired)
3. API Keys for both Legacy Conformity and CloudOne Conformity
   - **Note:** Both API Keys must have admin privileges

## How to use this tool

1) Create or choose an empty folder where you would like to install and run the tool.

2) Start a shell/terminal on the folder you just created or chosen.

3) Create a python3 virtual environment (minimum: python v3.7)
    ```
    python3 -m venv .venv
    ```

4) Activate the virtual environment
   ```
   source .venv/bin/activate
   ```

5) Install the tool
    ```
    pip install conformity-migration-tool
    ```
    In case you have installed the package before and need to upgrade, you can run
    ```
    pip install -U conformity-migration-tool
    ```
6) Configure the tool
    ```
    conformity-migration configure
    ```
    **Note:** Once you finish the tool configuration once, a file called **user-config.yml** with the settings you configured will be generated in the same folder, in case you need to re-run the tool.

7) If you have AWS accounts, you have the option to use this CLI for updating your `ExternalId`:
   ```
   conformity-migration-aws generate-csv <CSV_FILE>
   ```
   Update your CSV file with your AWS credentials. Then use the updated csv to run the command below:
   ```
   conformity-migration-aws update-stack --csv-file <CSV_FILE>
   ```
   You can also run this CLI to update an invidual account's stack, which is useful if you want to
   wrap it in your own script that will iterate through all your accounts. To find those options,
   please run this command:
   ```
   conformity-migration-aws update-stack --help
   ```

8)  Run the migration
    ```
    conformity-migration run
    ```
    If you already updated your AWS accounts' `ExternalId` beforehand as in step 8, then you can add this
    option below so it will stop prompting you to update your ExternalId manually:
    ```
    conformity-migration run --skip-aws-prompt
    ```


## Migration support
### Cloud Types
- [X] AWS account
  - **Note:** To grant access to CloudOne Conformity, user has to update the `ExternalId` parameter of CloudConformity stack of his/her AWS account. This can be done either manually or using the CLI `conformity-migration-aws` which is part of the conformity-migration-tool package.

- [X] Azure account
  - **Note:** User needs to specify App Registration Key so the tool can add the Active Directory to Conformity
- [ ] GCP account

### Organisation-Level Configurations
- [X] Users
  - **Note**: The tool will display other users that needs to be invited by the admin to CloudOne Conformity.
- [X] Groups
- [X] Communication channel settings
- [X] Profiles
- [X] Report Configs

### Group-Level Configurations
- [X] Report Configs

### Account-Level Configurations
- [X] Account tags
- [X] Conformity Bot settings
- [X] Account Rule settings
  - **Limitation:** The API only allows writing a single note to the rule so the tool won't be able to preserve the history of notes. The tool will instead combine history of notes into a single note before writing it.
- [X] Communication channel settings
- [X] Checks
  - **Limitation:** The API only allows writing a single note to the check so the tool won't be able to preserve the history of notes. In addition to that, API only allows a maximum of 200 characters of note. The tool will only get the most recent note and truncate it to 200 characters before writing it.
- [X] Report Configs


## Cleanup Cloud Conformity Account After Migration

### **⚠ WARNING: This commands will erase all the content in Cloud Conformity, be sure to migrate all the configure before**

Run the cleanup
```
conformity-migration empty-legacy
```

## Troubleshooting
If you encounter any errors in the execution, please [Create a New Issue](https://github.com/trendmicro/solutions-architect/issues/new?assignees=&labels=bug&template=bug_report.md&title=) describing the steps that you went through, the results expected, and the actual results that you got.

### Support logs
The tool automatically generates log files when an error is found. In the same folder that you ran the tool, you will find these files:

- ```conformity-migration-error.log``` -> Specific logs about errors encountered from the last runtime.

- ```conformity-migration.log``` -> General log information about the tool the last runtime.

**Note:** Please don't share these files publicly, they might contain sensitive information about your environment. In case you need to share for support purposes, mask sensitive information before sending it.


## Contributing

If you encounter a bug, think of a useful feature, or find something confusing
in the docs, please
[Create a New Issue](https://github.com/trendmicro/solutions-architect/issues/new/choose)!

We :heart: pull requests. If you'd like to fix a bug, contribute to a feature or
just correct a typo, please feel free to do so.

If you're thinking of adding a new feature, consider opening an issue first to
discuss it to ensure it aligns with the direction of the project (and potentially
save yourself some time!).