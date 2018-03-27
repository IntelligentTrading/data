import json
import logging
import sys
import time

import boto3
import schedule

import ccxt

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData

from settings import EXCHANGE_MARKETS, AWS_OPTIONS, AWS_SNS_TOPIC_ARN, PUBLISH_MESSSAGES, LOCAL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch tickers every 1 minute"

    def handle(self, *args, **options):
        logger.info("Getting ready to fetch tickers from exchanges")
        
        if LOCAL: # FIXME Remove this local part later. Now it's just for debug.
            fetch_and_process_all()
        else:
            schedule.every(1).minutes.do(fetch_and_process_all)
            # FIXME choose better scheduling later
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    logger.debug(str(e))
                    logger.info("Fetching shut down.")


# FIXME Reorganize code later. Better variable/functions names

def fetch_and_process_all():
    for exchange in EXCHANGE_MARKETS:
        tickers = fetch_tickers_from(exchange)

        save_to_db(tickers, exchange)

        symbols_info = process_tickers_to_standart_format(tickers, exchange)
        if PUBLISH_MESSSAGES:
            publish_message_to_queue(symbols_info)
 
def fetch_tickers_from(exchange_id):
    # we use ccxt: https://github.com/ccxt/ccxt/tree/master/python
    exchange = getattr(ccxt, exchange_id)()
    tickers = exchange.fetch_tickers()
    return tickers

def process_tickers_to_standart_format(tickers, exchange_id):
    # * Standart Format
    # symbols_info = [
    #     {   'source': 'poloniex',
    #         'category': 'last_price', # or 'quote_volume',
    #         'transaction_currency': 'BTC',
    #         'counter_currency': 'USDT',
    #         'value': 12345678,
    #         'timestamp': 1522066118.23
    #     }, ...
    # ]
    symbols_info = list()
    #logger.debug(tickers)
    for currency_pair, currency_info in tickers.items(): # DASH/BTC, BCH/USDT, REP/BTC
        logger.debug(f'Currencies for {exchange_id}: {currency_pair}')

        if currency_pair.endswith('BTC') or currency_pair.endswith('USDT'): # filtering
            print(f'currency_pair: {currency_pair}, info: {currency_info}')
            if 'last' in currency_info: # last_price
                symbols_info.append(standard_format_item(
                    source=exchange_id, category='price',
                    value=currency_info['last'],
                    currency_info=currency_info))
            if 'quoteVolume' in currency_info: # quote_volume
                symbols_info.append(standard_format_item(
                    source=exchange_id, category='quote_volume',
                    value=currency_info['quoteVolume'],
                    currency_info=currency_info))

    #logger.debug(f'Symbols info: {symbols_info}')
    logger.debug(f'Processed: {len(tickers)}')
    return symbols_info

def publish_message_to_queue(symbols_info):
    logger.debug(f"Sent message with {len(symbols_info)} items and size {sys.getsizeof(symbols_info)} bytes")

    aws = aws_client('sns')
    response = aws.publish(
        TopicArn=AWS_SNS_TOPIC_ARN,
        Message=json.dumps(symbols_info),
    )
    logger.debug(f"Published Messsage response: {response}")
    return response

def save_to_db(tickers, exchange_id):
    timestamp = tickers[list(tickers)[0]]['timestamp']/1000 # convert from timestamp in miliseconds
    ExchangeData.objects.create(
        source=exchange_id,
        data=tickers, # the exact json from the request data
        timestamp=timestamp,
    )
    logger.debug(f"Saved to db: {exchange_id}")


def standard_format_item(source, category, value, currency_info):
    currency_pair_list = currency_info['symbol'].split('/')
    return {
        'source': source,
        'category': category,
        'transaction_currency': currency_pair_list[0],
        'counter_currency': currency_pair_list[1],
        'value': value,
        'timestamp': currency_info['timestamp']/1000 # timestamp in miliseconds
    }

def aws_client(client_type):
    return boto3.client(
        client_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1',
    )
