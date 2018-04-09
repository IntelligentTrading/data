import json
import logging
import sys
import time
import threading

import boto3
import schedule

import ccxt

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.common.utilities.multithreading import start_new_thread

from settings import EXCHANGE_MARKETS, AWS_OPTIONS, AWS_SNS_TOPIC_ARN, PUBLISH_MESSSAGES, LOCAL
#from settings import ALL_COINS



logger = logging.getLogger(__name__)

# too noisy
logging.getLogger("ccxt.base.exchange").setLevel(logging.INFO)
logging.getLogger("botocore.endpoint").setLevel(logging.INFO)
logging.getLogger("boto3.resources.action").setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Fetch tickers every 1 minute"

    def handle(self, *args, **options):
        logger.info(f'>>> Getting ready to fetch tickers from: {", ".join(EXCHANGE_MARKETS)}')

        USDT_RATE = get_usd_price_for('BTC', 'ETH')

        #fetch_and_process_all(); return # one iteration for debug only
        
        schedule.every(1).minutes.do(fetch_and_process_all)
        while True:
            try:
                schedule.run_pending()
                time.sleep(10)
            except Exception as e:
                logger.debug(str(e))
                logger.info(">>> Fetching shut down.")


def fetch_and_process_all():
    for exchange in EXCHANGE_MARKETS:
        logger.debug(f'Starting thread with fetch_and_process_one({exchange})')
        fetch_and_process_one(exchange)
        #threading.Thread(target=fetch_and_process_one, args=(exchange,)).start()
    
    logger.info('\n>>> Waiting for next call of fetch_and_process_all')

def fetch_and_process_one(exchange):
    tickers = fetch_tickers_from(exchange)

    save_to_db(tickers, exchange)
    
    symbols_info = process_tickers_to_standart_format(tickers, exchange)
    publish_message_to_queue(json.dumps(symbols_info))


def fetch_tickers_from(exchange_id):
    # we use ccxt: https://github.com/ccxt/ccxt/tree/master/python
    exchange = getattr(ccxt, exchange_id)()
    tickers = exchange.fetch_tickers()
    return tickers

def process_tickers_to_standart_format(tickers, exchange_id):
    # * Standart Format
    # symbols_info = [
    #     {   'source': 'poloniex',
    #         'category': 'price', # or 'volume'
    #         'symbol': 'BTC/USDT' # LTC/BTC
    #         'value': 12345678,
    #         'timestamp': 1522066118.23
    #     }, ...
    # ]

    symbols_info = list()

    logger.info(f'Processing currencies for {exchange_id}')
    count_added = 0

    for symbol, symbol_info in tickers.items(): # symbol: DASH/BTC, BCH/USDT, REP/BTC
        #logger.debug(f'{symbol}')
        try:
            (transaction_currency, counter_currency) = symbol.split('/') # check format
        except ValueError:
            logger.debug(f'Skipping symbol: {symbol}')
            continue # skip malformed currency pairs


        # FIXME add filtering by volume
        if counter_currency in ('BTC', 'USDT', 'ETH') and enough_volume(symbol_info): # filtering
            # For debug
            if transaction_currency in ('BTC', 'ETH', 'DASH'):
                logger.debug(f'+Adding {symbol}\nInfo: {symbol_info}')
            # For debug end

            count_added += 1
            if 'last' in symbol_info: # last_price
                symbols_info.append(standard_format_item(
                    source=exchange_id, category='price',
                    value=symbol_info['last'],
                    symbol_info=symbol_info))
            if 'quoteVolume' in symbol_info: # quote_volume, mean volume in counter_currrency
                symbols_info.append(standard_format_item(
                    source=exchange_id, category='volume',
                    value=symbol_info['quoteVolume'],
                    symbol_info=symbol_info))
        # else:
        #     logger.debug(f'>> Filtered: {symbol}\n>>Info symbol_info')

    #logger.debug(f'Symbols info: {symbols_info}')
    logger.info(f'>>> Processed: {len(tickers)}, Added: {count_added} items')
    return symbols_info

def enough_volume(symbol_info):
    #print(f">>> Quote Volume: {symbol_info['quoteVolume']}")
    return True

def publish_message_to_queue(message, topic_arn=AWS_SNS_TOPIC_ARN):
    logger.debug(f"Publish message, size: {len(message)}")
    if PUBLISH_MESSSAGES:
        sns = aws_resource('sns')
        topic = sns.Topic(topic_arn)
        response = topic.publish(
            Message=message,
        )
        #logger.debug(f">>> Messsage published with response: {response}")
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


def standard_format_item(source, category, value, symbol_info):
    return {
        'source': source,
        'category': category, # 'price' or 'volume'
        'symbol': symbol_info['symbol'],
        'value': value,
        'timestamp': symbol_info['timestamp']/1000 # timestamp in miliseconds
    }

def aws_resource(resource_type):
    return boto3.resource(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name=AWS_OPTIONS['AWS_REGION'],
    )

def get_usd_price_for(*coins):
    usdt_rate = {}
    ccap = ccxt.coinmarketcap()
    ccap.load_markets()
    for coin in coins:
        usdt_rate[coin] = float(ccap.market(f'{coin}/USD')['info']['price_usd']) #ccap.fetch_ticker(f'{coin}/USD')['close']
    return usdt_rate
