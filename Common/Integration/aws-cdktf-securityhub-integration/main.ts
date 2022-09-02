import { Construct } from "constructs";
import { App, TerraformStack, TerraformOutput, TerraformVariable } from "cdktf";
import { AwsProvider, iam } from '@cdktf/provider-aws';
import { IamPolicyAttachment } from "@cdktf/provider-aws/lib/iam";

class secHubIntegration extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);


    const awsRegion = new TerraformVariable(this, 'awsRegion', {
      type: 'string',
      default: 'us-east-1',
      description: 'The AWS Region to be use'
    });

    const securityHubAccountId = new TerraformVariable(this, 'securityHubAccountId', {
      type: 'string',
      description: 'The ID of the Security Hub AWS account'
    });
    
    const cloudOneAccountId = new TerraformVariable(this, 'cloudOneAccountId', {
      type: 'string',
      description: 'The ID of the Cloud One account'
      // To get the Account ID, log in to the Cloud One and access this page: https://cloudone.trendmicro.com/account-selection, copy the ID related to the desired account
    });
    
    const securityHubProductARN = 'arn:aws:securityhub:'+awsRegion.value+':'+securityHubAccountId.value+':product/'+securityHubAccountId.value+'/default'
    const securityHubTmAwsAccountId = '868324285112'

    new AwsProvider(this, "aws", {
      region: awsRegion.value,
    });

    const createPolicy = new iam.IamPolicy(this, "policy", {
      namePrefix: "SecurityHub-Policy-",
      description: "SecurityHub Policy",
      tags: {
        Name: "SecurityHub-Iam-Policy"
      },
      policy: JSON.stringify({
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": [
                "securityhub:BatchImportFindings"
            ],
            "Resource": securityHubProductARN
          }
        ]
      }),
    });

    const createRole = new iam.IamRole(this, "role", {
      namePrefix: "SecurityHub-Role-",
      description: "IAM Role to allow BatchImportFindings to your security hub resources",
      tags: {
        Name: "SecurityHub-Iam-Role"
      },
      assumeRolePolicy: JSON.stringify({
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::"+securityHubTmAwsAccountId+":root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": cloudOneAccountId.value
                }
            }
          }
        ]
      }),
    });


    new IamPolicyAttachment(this, "policyAttachment", {
      name: "SecurityHub-Policy-Attachment",
      policyArn: createPolicy.arn,
      roles: [createRole.name]
    });

    new TerraformOutput(this, "aws_role_arn", {
      value: createRole.arn }
    )

    new TerraformOutput(this, "aws_policy_arn", {
      value: createPolicy.arn }
    )

  }}

const app = new App();
new secHubIntegration(app, "cdktf");
app.synth();
