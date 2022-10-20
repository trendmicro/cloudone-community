# custom-rule

Helps manage custom rules in C1 Conformity using 4 simple commands in the CLI:

    * create
    * get
    * update
    * delete

Additionally, the list command retrieves all custom rules in an organization.

Usage:
_ "./custom-rule.py help" for overall help
_ "./custom-rule.py command help" for help on the given command

## conformity terraform provider

The Conformity Terraform provider provides the ideal experience for automation scenarios using infrastructure as code:

https://registry.terraform.io/providers/trendmicro/conformity/latest/docs

# developing custom rules

The custom rules framework allows creating rich rulesets for evaluating resource configuration. The framework documentation is the ideal resource for understanding rule logic and other settings at:

https://cloudone.trendmicro.com/docs/conformity/in-preview-custom-rules-overview

All interactions with the tool require arguments taken from the Conformity Dashboard, your Cloud console and YAML files. The files are stored in the /workspace folder.

The following command will assist developing custom rules:

    * generate: provides a sample empty rule
    * run: runs a saved custom rule and provides all the data available about a resource
    * show-providers: lists all the platforms supported by Conformity
    * show-services: lists the services supported by a given platform
    * show-resource-types: lists the resources supported by Conformity on a given service

## process

    * Start by configuring the tool using the **configure** command
    * Create a YAML file with the rule settings. See the ~/examples folder for reference. Optionally, generate a sample rule using the **generate** command and start from there
    * Create the rule using the **create** command. The tool will create a new file; this new file will become your working file from now on.
    * Test the custom rule using the **run** command. The tool will create a .run.yaml file showing the outcome and resource data. You can use the resource data to further advance your rule design

It is recommended to work from within a source code editor and a terminal window.

If you prefer using Terraform see the ~/examples/terraform folder for reference.

# changes and issues?

Feel free to send a PR or raise an issue.
