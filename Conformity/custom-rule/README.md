# custom-rule

Helps manage and develop custom rules in C1 Conformity using the CLI.

The CLI commands are split in two groups: Management & Development. See below for further details.

Additionally './custom-rule.py configure --apiKey <Cloud One API Key> --region <Cloud One Region>' configures the tool for work.

Optionally './custom-rule.py configure --apiKey <Cloud One API Key> --region <Cloud One Region> --workspace <folder location>' lets you set your own working folder.

## management commands

'''
./custom-rule.py create --file <custom rule YAML file>
./custom-rule.py get --ruleId <custom rule id>
./custom-rule.py update --file <custom rule YAML file>
./custom-rule.py delete --ruleId
./custom-rule.py list
'''

## development commands

'''
./custom-rule.py run --ruleId <custom rule Id> --accountid <Conformity account id> --resourceId <Cloud Provider Resource Id>
./custom-rule.py generate
./custom-rule.py show-providers
./custom-rule.py show-services --provider <Conformity Cloud Provider>
./custom-rule.py show-resource-types --service <Conformity Service>
'''

## further help

**All** the commands will provide additional usage information if the '--help' switch is provided:
'''
./custom-rule.py create --help
./custom-rule.py get --help
./custom-rule.py update --help
./custom-rule.py delete --help
./custom-rule.py list --help
./custom-rule.py run --help
./custom-rule.py generate --help
./custom-rule.py show-providers --help
./custom-rule.py show-services --help
./custom-rule.py show-resource-types --help
'''

# developing custom rules

The custom rules framework allows creating rich rulesets for evaluating resource configuration. The framework documentation is the ideal resource for understanding how to express the rule logic that determines where resources PASS or FAIL the check:

https://cloudone.trendmicro.com/docs/conformity/in-preview-custom-rules-overview

## process

    * Configure the tool using './custom-rule.py configure --apiKey <API Key> --region <Cloud One Region>'. Optionally, you can include '--workspace <folder location>' to use to own working folder
    * Create a YAML file with the rule settings. You can use './custom-rule.py generate' to obtain an empty rule that can be populated with rule settings and logic as needed
    * Use './custom-rule.py show-providers', './custom-rule.py show-services' and './custom-rule.py show-resource-types' to get settings needed to run your rule against specific services and resource types
    * Create the rule using './custom-rule.py create --file <filename>'. The tool will respond by creating a new file called with the rule id, i.e: CUSTOM-a3b2n6.yaml. TIP: Use very simple logic at this point
    * Test the custom rule using './custom-rule.py run --ruleId <Custom Rule Id> --accountId <Conformity Account Id> --resource <Cloud Provider Resource Id>'. The tool respond by creating  '.run.yaml' file showing the outcome and resource data.
    * You can use the resource data to further advance your rule design by updating the rule using './custom-rule.py update --file <custom rule file>'

It is recommended to work from within a source code editor and a terminal window.

### example

The following example creates a very simple custom rule that validates that s3 buckets are not called 'test':

'''
./custom-rule.py configure --apiKey SAMPLEKEY --region trend-us-1
./custom-rule.py create --file s3bucket.yaml
./custom-rule.py run --ruleId <CUSTOM-RULE-ID> --accountId <Conformity ID of the AWS account> --resourceId <name of the s3 bucket in AWS>
./custom-rule.py update --file <CUSTOM-RULE-ID>.yaml
'''

#### custom rule file "s3bucket.yaml"

'''
name: "S3 Bucket Name should be valid - For Joy"
description: "Buckets must not be named Test - For Joy"
remediationNotes: "Rename the bucket"
service: "S3"
resourceType: "s3-bucket"
categories: - "operational-excellence"
severity: "HIGH"
provider: "aws"
enabled: true
attributes: - name: "bucketName"
path: "data.Name"
required: true
rules: - conditions:
any: - fact: "bucketName"
operator: "notEqual"
value: "Test"
event:
type: "Mis-named S3 bucket created"
'''

# changes and issues?

Feel free to send a PR or raise an issue.
