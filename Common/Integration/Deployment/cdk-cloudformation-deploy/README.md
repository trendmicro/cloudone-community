# CDK/CloudFormation project to deploy Cloud One Integrations - AWS Security Hub Connector  

This is a CDK project with a pre-generated CloudFormation template that can be used to deploy all the required IAM resources in a given AWS account to integrate Cloud One Integrations with AWS Security Hub.

## Requirements

Take note of your Cloud One account id.

## Deployment

### **Via CloudFormation dashboard**

Click [here](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://trendmicro-solutions-architect.s3.amazonaws.com/cloud-one-integrations-security-hub.template.yaml)

### **Via CloudFormation CLI**

```
export CLOUD_ONE_REGION=**YOUR-CLOUD-ONE-REGION-ID**
aws cloudformation create-stack --stack-name cloud-one-integrations-security-hub --parameters ParameterKey=CloudOneId,ParameterValue=$CLOUD_ONE_REGION --template-body file://cdk.out/cloud-one-integrations-security-hub.template.yaml --capabilities CAPABILITY_NAMED_IAM
```

### **Via CDK**

```
export CLOUD_ONE_REGION=**YOUR-CLOUD-ONE-REGION-ID**
cdk deploy --parameters CloudOneId=$CLOUD_ONE_REGION
```

## Next Features

- Add a Custom Resource to run the necessary API calls to register the connector in our backend.