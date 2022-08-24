
# Copyright (C) 2021 Trend Micro Inc. All rights reserved.

import json
import os
import sys
import boto3
import botocore
from botocore.config import Config
from botocore.exceptions import ClientError
import urllib.parse
import uuid
import datetime
import csv
import time

region = boto3.session.Session().region_name
s3_client_path = boto3.client('s3', region, config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))
s3_client_virtual = boto3.client('s3', region, config=Config(s3={'addressing_style': 'virtual'}, signature_version='s3v4'))

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
    sqs_url = SQS_URL
    sqs_region = sqs_url.split('.')[1]
    sqs_endpoint_url = 'https://sqs.{0}.amazonaws.com'.format(sqs_region)
    report_object_key = 'True' == os.environ.get('REPORT_OBJECT_KEY', 'False')
    object = {
        'S3': {
            'bucket': bucket_name,
            'object': object_name,
            'amzRequestID': amz_request_id,
        },
        'ScanID': str(uuid.uuid4()),
        'SNS' : SNS_ARN,
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

def request_scan(bucket, key):
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
    # print(f'AMZ request ID: {amz_request_id}, event time: {event_time}, URL:', presigned_url.split('?')[0])
    sqs_response = push_to_sqs(bucket, key, amz_request_id, presigned_url, event_time)
    # print(sqs_response)

def read_csv(file_name):
    keys = []
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', skipinitialspace=True)
        for row in reader:
           keys.append(row[3])
    return keys

if __name__ == "__main__":
    start_time = time.time()
    if len(sys.argv) != 5:
        print('usage: scan bucket_name csv_file_path SQS_scanner_queue_url SNS_results_topic_arn')
        sys.exit(0)
    bucket = sys.argv[1]
    csv_file = sys.argv[2]
    SQS_URL = sys.argv[3]
    SNS_ARN = sys.argv[4]
    keys = read_csv(csv_file)
    keys_length = len(keys)
    for index, key in enumerate(keys):
        percentage = (index / keys_length) * 100 
        print('Requesting scan for %s - %s%%' % (key, percentage))
        request_scan(bucket, key)
    print('Total time to scall all %s objects: %s seconds' % (keys_length, time.time() - start_time))