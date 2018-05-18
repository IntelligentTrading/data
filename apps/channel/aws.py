import boto3

from settings import AWS_OPTIONS



def aws_resource(resource_type):
    return boto3.resource(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name=AWS_OPTIONS['AWS_REGION'],
    )

def aws_client(resource_type):
    return boto3.client(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name=AWS_OPTIONS['AWS_REGION'],
    )
