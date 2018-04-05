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
from settings import ALL_COINS



logger = logging.getLogger(__name__)

logging.getLogger("ccxt.base.exchange").setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Fetch tickers every 1 minute"

    def handle(self, *args, **options):
        logger.info(f'>>> Getting ready to fetch tickers from: {", ".join(EXCHANGE_MARKETS)}')

        #fetch_and_process_all(); return # 1 iteration for debug only
        
        schedule.every(1).minutes.do(fetch_and_process_all)
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info(">>> Fetching shut down.")


def fetch_and_process_all():
    for exchange in EXCHANGE_MARKETS:
        tickers = fetch_tickers_from(exchange)

        save_to_db(tickers, exchange)

        symbols_info = process_tickers_to_standart_format(tickers, exchange)
        publish_message_to_queue(symbols_info)
       
        logger.info('\n>>> Waiting for next call of fetch_and_process_all')
 
def fetch_tickers_from(exchange_id):
    # we use ccxt: https://github.com/ccxt/ccxt/tree/master/python
    exchange = getattr(ccxt, exchange_id)()
    tickers = exchange.fetch_tickers()
    return tickers

def process_tickers_to_standart_format(tickers, exchange_id):
    # * Standart Format
    # symbols_info = [
    #     {   'source': 'poloniex',
    #         'category': 'price', # or 'volume',
    #         'transaction_currency': 'BTC',
    #         'counter_currency': 'USDT',
    #         'value': 12345678,
    #         'timestamp': 1522066118.23
    #     }, ...
    # ]

    symbols_info = list()

    logger.debug(f'Processing currencies for {exchange_id}')
    count_added = 0

    for currency_pair, currency_info in tickers.items(): # currency_pair: DASH/BTC, BCH/USDT, REP/BTC
        logger.debug(f'{currency_pair}')
        try:
            (transaction_currency, counter_currency) = currency_pair.split('/')
        except ValueError:
            continue # skip malformed currency pairs
#        if (transaction_currency in ALL_COINS) and (counter_currency in ('BTC', 'USDT', 'ETH')):
#        if currency_pair.endswith('BTC') or currency_pair.endswith('USDT'): # filtering
        if True: # process all currency pairs
            logger.debug(f'+Adding: {currency_pair}')
            count_added += 1
            # logger.debug(f'currency_pair: {currency_pair}, info: {currency_info}')
            if 'last' in currency_info: # last_price
                symbols_info.append(standard_format_item(
                    source=exchange_id, category='price',
                    value=currency_info['last'],
                    currency_info=currency_info))
            if 'quoteVolume' in currency_info: # quote_volume, mean volume in counter_currrency
                symbols_info.append(standard_format_item(
                    source=exchange_id, category='volume',
                    value=currency_info['quoteVolume'],
                    currency_info=currency_info))

    #logger.debug(f'Symbols info: {symbols_info}')
    logger.debug(f'>>> Processed: {len(tickers)}, Added: {count_added} items')
    return symbols_info

def publish_message_to_queue(symbols_info):
    logger.debug(f"Publish message: {len(symbols_info)} symbols, {sys.getsizeof(symbols_info)} bytes")
    if PUBLISH_MESSSAGES:
        sns = aws_resource('sns')
        topic = sns.Topic(AWS_SNS_TOPIC_ARN)
        response = topic.publish(
            Message=json.dumps(symbols_info)
        )
        logger.debug(f">>> Messsage published with response: {response}")
    else:
        logger.debug(f'>>> Simulated publishing')
        response = None
    return response


def save_to_db(tickers, exchange_id):
    timestamp = tickers[list(tickers)[0]]['timestamp']/1000 # convert from timestamp in miliseconds
    ExchangeData.objects.create(
        source=exchange_id,
        data=tickers, # the exact json from the ccxt
        timestamp=timestamp,
    )
    logger.debug(f">>> Saved to db: {exchange_id}")


def standard_format_item(source, category, value, currency_info):
    (transaction_currency, counter_currency) = currency_info['symbol'].split('/')
    #currency_pair_list = currency_info['symbol'].split('/')
    return {
        'source': source,
        'category': category, # 'price' or 'volume'
        'transaction_currency': transaction_currency,
        'counter_currency': counter_currency,
        'value': value,
        'timestamp': currency_info['timestamp']/1000 # timestamp in miliseconds
    }

def aws_resource(resource_type):
    return boto3.resource(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name=AWS_OPTIONS['AWS_REGION'],
    )
