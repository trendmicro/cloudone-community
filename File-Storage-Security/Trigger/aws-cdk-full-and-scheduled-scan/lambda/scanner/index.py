# Copyright (C) 2021 Trend Micro Inc. All rights reserved.

import json
import os
import logging
import boto3
import botocore
from botocore.config import Config
from botocore.exceptions import ClientError
import urllib.parse
import uuid
import datetime

sqs_url = os.environ['SQSUrl']
print('scanner queue URL: ' + sqs_url)
sqs_region = sqs_url.split('.')[1]
print('scanner queue region: ' + sqs_region)
sqs_endpoint_url = 'https://sqs.{0}.amazonaws.com'.format(sqs_region)
print('scanner queue endpoint URL: ' + sqs_endpoint_url)
report_object_key = 'True' == os.environ.get('REPORT_OBJECT_KEY', 'False')
print(f'report object key: {report_object_key}')

region = boto3.session.Session().region_name
s3_client_path = boto3.client('s3', region, config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))
s3_client_virtual = boto3.client('s3', region, config=Config(s3={'addressing_style': 'virtual'}, signature_version='s3v4'))

try:
    with open('version.json') as version_file:
        version = json.load(version_file)
        print(f'version: {version}')
except Exception as ex:
    print('failed to get version: ' + str(ex))

def create_presigned_url(bucket_name, object_name, expiration):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        s3_client = s3_client_path if '.' in bucket_name else s3_client_virtual
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        print('failed to generate pre-signed URL: ' + str(e))
        return None

    # The response contains the presigned URL which is sensitive data
    return response


def push_to_sqs(bucket_name, object_name, amz_request_id, presigned_url, event_time):
    object = {
        'S3': {
            'bucket': bucket_name,
            'object': object_name,
            'amzRequestID': amz_request_id,
        },
        'ScanID': str(uuid.uuid4()),
        'SNS' : os.environ['SNSArn'],
        'URL': presigned_url,
        'ModTime': event_time,
        'ReportObjectKey': report_object_key
    }
    try:
        session = boto3.session.Session(region_name=sqs_region)
        sqs = session.resource(service_name='sqs', endpoint_url=sqs_endpoint_url)
        queue = sqs.Queue(url=sqs_url)
        response = queue.send_message(MessageBody=json.dumps(object))
        return response
    except ClientError as e:
        print('failed to push SQS message: ' + str(e))
        return None

def is_folder(key):
    return key.endswith('/')

def handle_step_functions_event(bucket, key):
    key = urllib.parse.unquote_plus(key)
    amz_request_id = "f"
    event_time = datetime.datetime.utcnow().isoformat() # ISO-8601 format, 1970-01-01T00:00:00.000Z, when Amazon S3 finished processing the request

    if is_folder(key):
        print('Skip scanning for folder.')
        return

    presigned_url = create_presigned_url(
        bucket,
        key,
        expiration = 60 * 60 # in seconds
    )
    print(f'AMZ request ID: {amz_request_id}, event time: {event_time}, URL:', presigned_url.split('?')[0])
    sqs_response = push_to_sqs(bucket, key, amz_request_id, presigned_url, event_time)
    print(sqs_response)

def lambda_handler(event, context):

    bucket = event['bucket']
    key = event['key']
    handle_step_functions_event(bucket, key)