import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam'

export class CloudOneWorkloadSecurityIamStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const externalId = new cdk.CfnParameter(this, 'ExternalId', {
      description: 'Enter the external ID you retrieved from the manager earlier.'
    })
    
    const accountId = new cdk.CfnParameter(this, 'AccountId', {
      description: 'Enter Cloud One Workload Security Account ID.',
      default: '147995105371'
    })

    const policy = new iam.ManagedPolicy(this, 'Cloud-one-workload-security-policy', {
      statements: [
        new iam.PolicyStatement({
          sid: 'cloudconnector',
          actions: [
            'ec2:DescribeImages',
            'ec2:DescribeInstances',
            'ec2:DescribeRegions',
            'ec2:DescribeSubnets',
            'ec2:DescribeTags',
            'ec2:DescribeVpcs',
            'ec2:DescribeAvailabilityZones',
            'ec2:DescribeSecurityGroups',
            'workspaces:DescribeWorkspaces',
            'workspaces:DescribeWorkspaceDirectories',
            'workspaces:DescribeWorkspaceBundles',
            'workspaces:DescribeTags',
            'iam:ListAccountAliases',
            'iam:GetRole',
            'iam:GetRolePolicy'
          ],
          effect: iam.Effect.ALLOW,
          resources: ['*'],
        })
      ]
    });
  
    const role = new iam.Role(this, 'Cloud-one-workload-security-role', {
      assumedBy: new iam.AccountPrincipal(accountId.valueAsString),
      externalIds: [
        externalId.valueAsString
      ],
      managedPolicies: [
        policy
      ],
    });

    const roleArn = new cdk.CfnOutput(this, 'Role ARN', {
      value: role.roleArn
    });
  }
}
