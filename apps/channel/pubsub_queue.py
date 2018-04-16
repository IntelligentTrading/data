import logging

import boto3

from settings import AWS_OPTIONS, PUBLISH_MESSSAGES



logger = logging.getLogger(__name__)
# boto too noisy
#logging.getLogger("botocore.endpoint").setLevel(logging.INFO)
#logging.getLogger("boto3.resources.action").setLevel(logging.INFO)
logging.getLogger("boto3").setLevel(logging.INFO)
logging.getLogger("botocore").setLevel(logging.INFO)


def publish_message_to_queue(message, topic_arn):
    logger.debug(f"Publish message, size: {len(message)}")
    if PUBLISH_MESSSAGES:
        sns = aws_resource('sns')
        topic = sns.Topic(topic_arn)
        response = topic.publish(
            Message=message,
        )
        logger.debug(f">>> Messsage published with response: {response}")
    else:
        logger.debug(f'>>> Simulating publishing')
        response = None
    return response



def aws_resource(resource_type):
    return boto3.resource(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name=AWS_OPTIONS['AWS_REGION'],
    )
