import { Construct } from 'constructs';
import { CfnCondition, CfnOutput, CfnParameter, Duration, Fn, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as stepfunctions from 'aws-cdk-lib/aws-stepfunctions';
import * as fs from 'fs';

export class FssFullScanStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const bucketNameInput = new CfnParameter(this, 'BucketName', {
      type: 'String',
      description: 'Name of a bucket that you want to full scan. Make sure you have FSS Storage Stack deployed around it already.'
    })

    const queueArnInput = new CfnParameter(this, 'ScannerQueueArn', {
      type: 'String',
      description: 'ARN of the ScannerQueue queue. Something like arn:aws:sqs:us-east-1:123456789012:All-in-one-TM-FileStorageSecurity-ScannerStack-IT1V5O-ScannerQueue-1IOQHTGGGZYFL'
    });

    const sqsUrlInput = new CfnParameter(this, 'ScannerQueueUrl', {
      type: 'String',
      description: 'URL of the ScannerQueue queue. Something like https://sqs.us-east-1.amazonaws.com/123456789012/All-in-one-TM-FileStorageSecurity-ScannerStack-IT1V5O-ScannerQueue-1IOQHTGGGZYFL'
    });

    const topicArnInput = new CfnParameter(this, 'ScanResultTopicArn', {
      type: 'String',
      description: 'ARN of ScanResultTopic topic. Something like arn:aws:sns:us-east-1:123456789012:All-in-one-TM-FileStorageSecurity-StorageStack-1E00QCLBZW7M4-ScanResultTopic-1W7RZ7PBZZUJO'
    });

    const schedule = new CfnParameter(this, 'Schedule', {
      type: 'String',
      description: 'Set a schedule for full scan. If empty, there will not be a scheduled scan. Defaults to empty. More info at: https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents-expressions.html',
      default: '',
    });

    const setSchedule = new CfnCondition(this, 'SetSchedule', {
      expression: Fn.conditionNot(Fn.conditionEquals('', schedule.valueAsString))
    })

    const bucket = s3.Bucket.fromBucketName(this, 'Bucket', bucketNameInput.valueAsString);
    const queueArn = queueArnInput.valueAsString;
    const sqsUrl = sqsUrlInput.valueAsString;
    const topicArn = topicArnInput.valueAsString;

    // State Bucket
    const stateBucket = new s3.Bucket(this, 'StateBucket', {})

    // Paginator Function
    const paginatorExecutionRole = new iam.Role(this, 'PaginatorExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')]
    });

    paginatorExecutionRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [bucket.bucketArn],
      actions: ['s3:ListBucket'],
    }));

    const paginatorFunction = new lambda.Function(this, 'PaginatorFunction', {
      runtime: lambda.Runtime.NODEJS_16_X,
      architecture: lambda.Architecture.ARM_64,
      handler: 'index.lambda_handler',
      role: paginatorExecutionRole,
      timeout: Duration.minutes(15),
      memorySize: 1024,
      environment: {
        'STATE_BUCKET': stateBucket.bucketName,
      },
      code: lambda.Code.fromInline(fs.readFileSync('./lambda/paginator/index.js').toString())
    });
    stateBucket.grantWrite(paginatorFunction);

    // Filter Function
    const filterExecutionRole = new iam.Role(this, 'FilterExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')]
    });

    const filterFunction = new lambda.Function(this, 'FilterFunction', {
      runtime: lambda.Runtime.NODEJS_16_X,
      architecture: lambda.Architecture.ARM_64,
      handler: 'index.lambda_handler',
      role: filterExecutionRole,
      timeout: Duration.minutes(15),
      memorySize: 512,
      environment: {
        'BUCKET_NAME': bucket.bucketName,
      },
      code: lambda.Code.fromInline(fs.readFileSync('./lambda/filter/index.js').toString())
    });
    stateBucket.grantReadWrite(filterFunction);

    // Scanner Function
    const scanOneObjectExecutionRole = new iam.Role(this, 'ScanOneObjectExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')]
    });

    scanOneObjectExecutionRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [`${bucket.bucketArn}/*`],
      actions: ['s3:GetObject', 's3:PutObjectTagging'],
    }));

    scanOneObjectExecutionRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [queueArn],
      actions: ['sqs:SendMessage'],
    }));

    const scanOneObjectFunction = new lambda.Function(this, 'ScanOneObjectFunction', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'index.lambda_handler',
      role: scanOneObjectExecutionRole,
      timeout: Duration.minutes(1),
      memorySize: 128,
      environment: {
        'SNSArn': topicArn,
        'SQSUrl': sqsUrl,
      },
      code: lambda.Code.fromInline(fs.readFileSync('./lambda/scanner/index.py').toString())
    });

    // ScannerLoop Step Function
    const scannerLoopExecutionRole = new iam.Role(this, 'ScanStarterExecutionRole', {
      assumedBy: new iam.ServicePrincipal('states.amazonaws.com')
    });

    scannerLoopExecutionRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [scanOneObjectFunction.functionArn,filterFunction.functionArn],
      actions: ['lambda:InvokeFunction'],
    }));
    
    const scannerLoopStateMachineName = 'ScannerLoopStateMachine';
    const scannerLoopStepFunction = new stepfunctions.CfnStateMachine(this, "ScannerLoopStepFunction", {
      roleArn: scannerLoopExecutionRole.roleArn,
      stateMachineName: scannerLoopStateMachineName,
      definitionString: `
      {
        "Comment": "A machine that loops trough all files a bucket to scan them with File Storage Security.",
        "StartAt": "Filter first 1000 keys to scan",
        "States": {
          "Filter first 1000 keys to scan": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
              "Payload.$": "$",
              "FunctionName": "${filterFunction.functionArn}"
            },
            "Retry": [
              {
                "ErrorEquals": [
                  "Lambda.ServiceException",
                  "Lambda.AWSLambdaException",
                  "Lambda.SdkClientException"
                ],
                "IntervalSeconds": 2,
                "MaxAttempts": 6,
                "BackoffRate": 2
              }
            ],
            "Next": "Parallel"
          },
          "Parallel": {
            "Type": "Parallel",
            "Branches": [
              {
                "StartAt": "Map",
                "States": {
                  "Map": {
                    "Type": "Map",
                    "End": true,
                    "Parameters": {
                      "key.$": "$$.Map.Item.Value",
                      "bucket.$": "$.bucket"
                    },
                    "Iterator": {
                      "StartAt": "Scan a Object",
                      "States": {
                        "Scan a Object": {
                          "Type": "Task",
                          "Resource": "arn:aws:states:::lambda:invoke",
                          "OutputPath": "$.Payload",
                          "Parameters": {
                            "Payload.$": "$",
                            "FunctionName": "${scanOneObjectFunction.functionArn}"
                          },
                          "Retry": [
                            {
                              "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException"
                              ],
                              "IntervalSeconds": 2,
                              "MaxAttempts": 6,
                              "BackoffRate": 2
                            }
                          ],
                          "End": true
                        }
                      }
                    },
                    "ItemsPath": "$.keys"
                  }
                }
              },
              {
                "StartAt": "Are there keys left?",
                "States": {
                  "Are there keys left?": {
                    "Type": "Choice",
                    "Choices": [
                      {
                        "Variable": "$.remainingKeysLength",
                        "NumericGreaterThan": 0,
                        "Comment": "Yes",
                        "Next": "Re-execute with the remaining keys."
                      }
                    ],
                    "Default": "Pass"
                  },
                  "Re-execute with the remaining keys.": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::states:startExecution",
                    "Parameters": {
                      "StateMachineArn": "arn:${Stack.of(this).partition}:states:${Stack.of(this).region}:${Stack.of(this).account}:stateMachine:${scannerLoopStateMachineName}",
                      "Input": {
                        "stateBucket.$": "$.stateBucket",
                        "stateKey.$": "$.stateKey",
                        "limit.$": "$.limit",
                        "bucket.$": "$.bucket",
                        "AWS_STEP_FUNCTIONS_STARTED_BY_EXECUTION_ID.$": "$$.Execution.Id"
                      }
                    },
                    "End": true
                  },
                  "Pass": {
                    "Type": "Pass",
                    "End": true,
                    "Result": {}
                  }
                }
              }
            ],
            "End": true
          }
        }
      }
      `,
    });

    scannerLoopExecutionRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [scannerLoopStepFunction.attrArn],
      actions: ['states:StartExecution'],
    }));

    // Full Scan Starter Step Function
    const fullScanStarterExecutionRole = new iam.Role(this, 'FullScanStarterExecutionRole', {
      assumedBy: new iam.ServicePrincipal('states.amazonaws.com')
    });

    fullScanStarterExecutionRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [paginatorFunction.functionArn],
      actions: ['lambda:InvokeFunction'],
    }));

    fullScanStarterExecutionRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [scannerLoopStepFunction.attrArn],
      actions: ['states:StartExecution'],
    }));

    const fullScanStarterStateMachineName = 'fullScanStarterStateMachine';
    const fullScanStarterLoopStepFunction = new stepfunctions.StateMachine(this, "FullScanStarterLoopStepFunction", {
      role: fullScanStarterExecutionRole,
      stateMachineName: fullScanStarterStateMachineName,
      definition: new stepfunctions.Pass(this, 'StartState'),
    });

    // Handling the incapability of stepfunctions.StateMachine having a string as its definition.
    const cfnFullScanStarterLoopStepFunction = fullScanStarterLoopStepFunction.node.defaultChild as stepfunctions.CfnStateMachine;
    cfnFullScanStarterLoopStepFunction.definitionString =  `
      {
        "Comment": "Kicks of a Full Scan using File Storage Security.",
        "StartAt": "List all keys in bucket",
        "States": {
          "List all keys in bucket": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
              "FunctionName": "${paginatorFunction.functionArn}",
              "Payload": {
                "bucket": "${bucket.bucketName}"
              }
            },
            "Retry": [
              {
                "ErrorEquals": [
                  "Lambda.ServiceException",
                  "Lambda.AWSLambdaException",
                  "Lambda.SdkClientException"
                ],
                "IntervalSeconds": 2,
                "MaxAttempts": 6,
                "BackoffRate": 2
              }
            ],
            "Next": "Start Scanner Flow"
          },
          "Start Scanner Flow": {
            "Type": "Task",
            "Resource": "arn:aws:states:::states:startExecution",
            "Parameters": {
              "StateMachineArn": "${scannerLoopStepFunction.attrArn}",
              "Input": {
                "stateKey.$": "$.stateKey",
                "bucket.$": "$.bucket",
                "stateBucket.$": "$.stateBucket",
                "limit.$": "$.limit",
                "AWS_STEP_FUNCTIONS_STARTED_BY_EXECUTION_ID.$": "$$.Execution.Id"
              }
            },
            "End": true
          }
        }
      }
      `
   
    const scanOnSchedule = new events.Rule(this, 'ScanOnSchedule', {
      schedule: events.Schedule.expression(schedule.valueAsString),
      targets: [new targets.SfnStateMachine(fullScanStarterLoopStepFunction, {})],
    });
    const cfnScanOnSchedule = scanOnSchedule.node.defaultChild as events.CfnRule;
    cfnScanOnSchedule.cfnOptions.condition = setSchedule;

    new CfnOutput(this, 'FullScanFunctionPage', {
      value: `https://${this.region}.console.aws.amazon.com/states/home?region=${this.region}#/statemachines/view/arn:${this.partition}:states:${Stack.of(this).region}:${Stack.of(this).account}:stateMachine:${fullScanStarterStateMachineName}`,
    });

  };
}