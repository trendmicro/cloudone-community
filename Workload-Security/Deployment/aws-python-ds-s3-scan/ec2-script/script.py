import logging
import boto3
import time
import base64
import gzip
import struct
import re
import os
import json



# Initializing AWS resources
aws_region = os.environ['AWS_REGION']
queue_url = os.environ['SQS_URL']
sns_topic = os.environ['SNS_TOPIC']
sqs = boto3.resource('sqs',aws_region)
queue = sqs.Queue(queue_url)
s3_resource = boto3.resource('s3', region_name=aws_region)



# Initializing variables
max_queue_messages = 1
files_count = 0
bucket_prefix = 'cf'
body = ""
t = time.time()
d = os.chdir('/tmp')

# Loop for function call
while True:
    print("Checking queue...")
    messages_to_delete = []
    messages = queue.receive_messages(MaxNumberOfMessages=max_queue_messages)

    # Check if there is a messages on SQS
    if len(messages) == 0:
        print("No more messages, waiting 5 seconds")
        time.sleep(5)
        continue

    # Loop for SQS messages
    for message in messages:
        print('Message found!')
        body = json.loads(message.body)
        body = json.loads(body["Message"])
        if "Records" in body:
            bucket_name = body["Records"][0]["s3"]["bucket"]["name"]
            cflog_filekey = body["Records"][0]["s3"]["object"]["key"]
            print (bucket_name)
            print (cflog_filekey)
            print('Downloading the message  {} '.format(cflog_filekey))
            t2 = time.time()
            try:
                s3_resource.Bucket(bucket_name).download_file(cflog_filekey, "/scan/" + cflog_filekey)
                break
            except (FileNotFoundError, IOError):
                print("Malware Econtrado!")
                sns = boto3.client('sns',aws_region)
                sns_message = {
                    'bucket': bucket_name,
                    'file': cflog_filekey
                }

                response = sns.publish(
                    TopicArn=sns_topic,
                    Message= json.dumps({
                        'default': json.dumps(sns_message)
                    }),
                    Subject='Malware Found',
                    MessageStructure='json',
                    MessageAttributes={}
                )

                print('Download complete, in %.5f seconds' % (time.time() - t2))
                print(message)

            messages_to_delete.append({'Id': message.message_id,
                                       'ReceiptHandle': message.receipt_handle})
            print("%.5f" % (time.time() - t))

        print('Deleting messages...')
        if len(messages_to_delete) > 0:
            delete_response = queue.delete_messages(Entries=messages_to_delete)
