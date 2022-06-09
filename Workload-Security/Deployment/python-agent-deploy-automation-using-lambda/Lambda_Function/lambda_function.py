import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("logging setup complete")
#logging.getLogger('botocore').setLevel(logging.DEBUG)
#logging.getLogger('boto3').setLevel(logging.DEBUG)

def lambda_handler(event, context):
    logger.info('initializing for instanceid: ' + event['detail']['instance-id'])
    #get InstanceID from the EC2 that generated the log in CloudWatch
    instanceid = event['detail']['instance-id']

    #Wait EC2 to be with status Running
    ec2_resource = boto3.resource('ec2')
    instance = ec2_resource.Instance(instanceid)
    instance.wait_until_running()

    #Wait Instance to be with Status check to be ready (2/2)
    ec2_client = boto3.client('ec2')
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instanceid])

    logger.info("instance " + instanceid + " is running with status ready 2/2")

    #get the Instance Profile (ARN) from the EC2 if it has already
    arn_instance_profile = instance.iam_instance_profile

    #Check if the EC2 has the Tag InstallDSA if not add Tag Install DSA with Value 'Yes'
    if instance.tags == None:
        logger.info("instance " + instanceid + " has no tags; adding")
        #Call the function addTag
        addTag(ec2_client, instanceid)
    else:
        #Check if there are any Tag associated with the Ec2 with the name InstallDSA and with the Value set up as "No" or "no", if yes stop the script
        for tags in instance.tags:
            if tags['Key'] == "InstallDSA":
                if (tags["Value"] == 'No') or (tags["Value"] == 'no') or (tags["Value"] == 'NO'):
                    #If the tag Install DSA is no exit the lambda Function
                    logger.info("instance " + instanceid + " has tag InstallDSA == no; aborting")
                    return 0
                elif (tags["Value"] != 'yes') or (tags["Value"] != 'Yes') or (tags["Value"] != 'YES'):
                    addTag(ec2_client, instanceid)
                    break

    if arn_instance_profile == None:
        #If EC2 does not have Instance Profile applied we will attach an instance profile created from the CloudFormation with the properly policy permision to run SSM remote commands
        #Get values from Environment variables created by the CloudFormation process
        arn_instance_profile_from_CF = os.environ['InstanceProfiletoEC2Arn']
        name_instance_profile_from_CF = os.environ['InstanceProfiletoEC2Name']
        logger.info("instance " + instanceid + " has no instance profile; fixing it with " + arn_instance_profile_from_CF + " named " + name_instance_profile_from_CF)

        #Apply one InstanceProfile/Role to the EC2
        attach_instance_profile_response = ec2_client.associate_iam_instance_profile(
            IamInstanceProfile={
                'Arn': arn_instance_profile_from_CF,
                'Name': name_instance_profile_from_CF
            },
            InstanceId=instanceid
        )

    else:
        #get the instance profile name from insntance profile object with Arn and ID
        name_instance_profile = arn_instance_profile['Arn']
        name_instance_profile = name_instance_profile.split('/')
        name_instance_profile = name_instance_profile[1]

        #create iam resource to get the role associated with the instance profile
        iam = boto3.resource('iam')
        instance_profile_info = iam.InstanceProfile(name_instance_profile)
        ec2_role_attached = instance_profile_info.roles_attribute
        role_name_attached_to_ec2 = ec2_role_attached[0]['RoleName']

        #get the Managed Policy Name created by CloudFormation
        arn_managed_policy_to_attach_to_role = os.environ['PolicyName']

        #Attaches the specified managed policy to the specified IAM role.
        iam_client = boto3.client('iam')
        iam_attach_response = iam_client.attach_role_policy(
        PolicyArn=arn_managed_policy_to_attach_to_role,
        RoleName=role_name_attached_to_ec2,
        )
        logger.info("instance " + instanceid + " was attached with Managed Policy " + arn_managed_policy_to_attach_to_role )

    return 0

def addTag(ec2_client, instanceid):
    #Use function from boto3 to add Tag to the EC2
    logger.info("instance " + instanceid + " is getting the InstallDSA tag")
    response = ec2_client.create_tags(
                Resources=[
                    instanceid,
                ],
                Tags=[
                    {
                        'Key': 'InstallDSA',
                        'Value': 'Yes'
                    },
                ]
            )
