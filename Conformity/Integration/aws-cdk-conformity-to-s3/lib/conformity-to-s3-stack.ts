import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as s3 from '@aws-cdk/aws-s3';
import * as iam from '@aws-cdk/aws-iam';
import * as sns from '@aws-cdk/aws-sns';
import * as sqs from '@aws-cdk/aws-sqs';
import * as kms from '@aws-cdk/aws-kms';
import * as snsEventSource from '@aws-cdk/aws-lambda-event-sources';

const CONFORMITY_AWS_ACCOUNT = 717210094962;

export class ConformityToS3Stack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, 'conformity-to-s3-bucket');

    const key = new kms.Key(this, 'conformity-to-s3-key', {
      description: 'Key used for the Conformity to SNS integration.',
      policy: new iam.PolicyDocument({
        statements: [ new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          principals: [
            new iam.AccountPrincipal(CONFORMITY_AWS_ACCOUNT)
          ],
          actions: [
            'kms:Encrypt',
            'kms:Decrypt',
            'kms:ReEncrypt*',
            'kms:GenerateDataKey*',
            'kms:DescribeKey'
          ],
          resources: [
            '*'
          ]
        })]
      })
    })

    const topic = new sns.Topic(this, 'conformity-to-s3-topic', {
      masterKey: key,
    }); 
    topic.addToResourcePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      principals: [
        new iam.AccountPrincipal(CONFORMITY_AWS_ACCOUNT)
      ],
      actions: [
        'SNS:Publish'
      ],
      resources: [
        topic.topicArn
      ]
    }));

    const deadLetterQueue = new sqs.Queue(this, 'conformity-to-s3-deadLetterQueue', {
      encryptionMasterKey: key
    });

    const func = new lambda.Function(this, 'conformity-to-s3-function', {
      runtime: lambda.Runtime.NODEJS_12_X,
      handler: 'index.handler',
      environment: {
        'DESTINATION_BUCKET': bucket.bucketName
      },
      code: lambda.Code.fromInline(
        `
        const AWS = require( 'aws-sdk' );
        const S3  = new AWS.S3();
        
        exports.handler = async (event) => {
        
            if (!process.env.DESTINATION_BUCKET) {
                throw "DESTINATION_BUCKET env variable missing";
            }
        
            let message = JSON.parse(event.Records[0].Sns.Message);
                message = [message]; // keep the format as Array so the file format can cater for multiple checks
                message = JSON.stringify(message, null, 2);
        
            const params = {
                 Bucket: process.env.DESTINATION_BUCKET,
                 Key: \`` + '${Date.now()}' + `.json\`,
                 Body: message
            };
        
            return S3.putObject(params).promise();
        
        };
        
        `
      )
    });
    func.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        's3:PutObject',
        's3:PutBucketAcl'
      ],
      resources: [
        `arn:aws:s3:::${bucket.bucketName}`,
        `arn:aws:s3:::${bucket.bucketName}/*`
      ]
    }));
    func.addEventSource(new snsEventSource.SnsEventSource(topic, {
      deadLetterQueue: deadLetterQueue
    }));

    new cdk.CfnOutput(this, "EventsBucket", {
      value: bucket.bucketName,
      description: 'Bucket name that hosts all events'
    });

    new cdk.CfnOutput(this, "TopicARN", {
      value: topic.topicArn,
      description: 'SNS Topic ARN to be used in Conformity dashboard'
    });

  }
}
