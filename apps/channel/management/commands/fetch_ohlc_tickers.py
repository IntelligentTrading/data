import json
import logging
import time
import threading

import schedule

import ccxt

from django.core.management.base import BaseCommand

from apps.channel.tickers import Tickers, get_usdt_rates_for, to_satoshi_int
from apps.channel.pubsub_queue import publish_message_to_queue

from settings import EXCHANGE_MARKETS, AWS_SNS_TOPIC_ARN, SNS_PRICES_BATCH_SIZE
from settings import TICKERS_MINIMUM_USD_VOLUME
from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES



logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Fetch tickers every 1 minute"

    def handle(self, *args, **options):
        logger.info(f'>>> Getting ready to fetch ohlc tickers from: {", ".join(EXCHANGE_MARKETS)}')

        usdt_rates = get_usdt_rates_for('BTC', 'ETH')

        #fetch_and_process_all_exchanges(usdt_rates); return # one iteration for debug only

        schedule.every(1).minutes.do(fetch_and_process_all_exchanges, usdt_rates)

        keep_going = True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(10)
            except Exception as e:
                logger.debug(str(e))
                logger.info(">>> Fetching shut down")
                keep_going = False


def fetch_and_process_all_exchanges(usdt_rates):
    for exchange in EXCHANGE_MARKETS:
        logger.debug(f'Starting fetch_and_process_one({exchange})')
        threading.Thread(target=fetch_and_process_one, args=(exchange, usdt_rates)).start()
    logger.info('\n>>> Waiting for next call of fetch_and_process_all_exchanges')


def fetch_and_process_one(exchange, usdt_rates):
    tickers = Tickers(exchange=exchange, usdt_rates=usdt_rates, minimum_volume_in_usd=TICKERS_MINIMUM_USD_VOLUME)
    tickers.run()

    send_ohlc_data_to_queue(tickers)


def send_ohlc_data_to_queue(tickers_object, batch_size = SNS_PRICES_BATCH_SIZE):
    message_value = []
    for symbol, symbol_info in tickers_object.tickers.items():
        try:
            (transaction_currency, counter_currency) = symbol.split('/') # check format
        except ValueError:
            logger.debug(f'Skipping symbol: {symbol}')
            continue # skip malformed currency pairs

        if tickers_object._symbol_allowed(symbol_info=symbol_info, \
            usdt_rates=tickers_object.usdt_rates, \
            minimum_volume_in_usd=tickers_object.minimum_volume_in_usd):

            message_value.append({
                'source': tickers_object.exchange,
                'symbol': symbol_info['symbol'],
                'timestamp': symbol_info['timestamp']/1000, # timestamp in miliseconds,
                'popen': symbol_info['open'],
                'high': symbol_info['high'],
                'low': symbol_info['low'],
                'close': symbol_info['close'],
                'bvolume': symbol_info['baseVolume'],
                'average': symbol_info['average'],
            })

    # send messages in batches
    for i in range(0, len(message_value), batch_size):
        message_value_batch = message_value[i:i+batch_size]
        #print(f"batch_{i}> size:{len(message_value_batch)}")
        publish_message_to_queue(message=json.dumps(message_value_batch), topic_arn=AWS_SNS_TOPIC_ARN, subject="ohlc_prices")
