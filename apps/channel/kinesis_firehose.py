import logging
import json

import boto3

from apps.channel.aws import aws_client
from settings import PUBLISH_HISTORY



logger = logging.getLogger(__name__)
# boto too noisy
# logging.getLogger("boto3").setLevel(logging.INFO)
# logging.getLogger("botocore").setLevel(logging.INFO)

def put_record_to_kinesis_firehose_stream(record_dict, stream_name, client):
    logger.debug(f"Put record to Kinesis stream: {record_dict}")
    if PUBLISH_HISTORY:
        response = client.put_record(
            DeliveryStreamName=stream_name,
            Record={
                'Data': json.dumps(record_dict).encode('ascii')
            }
        )
        logger.debug(f">>> Record put to Kinesis with response: {response}")
    else:
        logger.debug(f'>>> Simulating putting record to Kinesis')
        response = None
    return response
