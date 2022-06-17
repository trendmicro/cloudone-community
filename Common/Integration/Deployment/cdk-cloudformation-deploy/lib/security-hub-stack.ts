import { CfnOutput, CfnParameter, Stack, StackProps } from 'aws-cdk-lib';
import { AccountPrincipal, Effect, ManagedPolicy, Policy, PolicyStatement, Role } from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class SecurityHubStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const CLOUD_ONE_INTEGRATIONS_AWS_ACCOUNT_ID = '868324285112';

    const cloudOneId = new CfnParameter(this, 'CloudOneId', {
      type: 'String',
      description: 'Cloud One Account id'
    })

    const policy = new ManagedPolicy(this, 'Policy', {
      statements: [
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ["securityhub:BatchImportFindings"],
          resources: [`arn:${Stack.of(this).partition}:securityhub:${Stack.of(this).region}:${Stack.of(this).account}:*`]
        })
      ]
    })

    const role = new Role(this, 'Role', {
      assumedBy: new AccountPrincipal(CLOUD_ONE_INTEGRATIONS_AWS_ACCOUNT_ID),
      externalIds: [cloudOneId.valueAsString],
      managedPolicies: [policy]
    })

    new CfnOutput(this, 'RoleArn', {
      value: role.roleArn
    })
  }
}
