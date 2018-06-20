import logging

import boto3

from apps.channel.aws import aws_resource
from settings import PUBLISH_MESSSAGES



logger = logging.getLogger(__name__)
# boto too noisy
#logging.getLogger("botocore.endpoint").setLevel(logging.INFO)
#logging.getLogger("boto3.resources.action").setLevel(logging.INFO)
logging.getLogger("boto3").setLevel(logging.INFO)
logging.getLogger("botocore").setLevel(logging.INFO)


def publish_message_to_queue(message, topic_arn, subject=''):
    logger.debug(f"Publish message, size: {len(message)}")
    if PUBLISH_MESSSAGES:
        sns = aws_resource('sns')
        topic = sns.Topic(topic_arn)
        response = topic.publish(
            Message=message,
            Subject=subject,
        )
        logger.debug(f">>> Messsage {subject} published with response: {response}")
    else:
        logger.debug(f'>>> Simulating publishing {subject}')
        response = None
    return response
