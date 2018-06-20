import json
import logging
import sys
import time
import threading

import schedule

import ccxt

from django.core.management.base import BaseCommand
#from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models import HistoryPrice

from apps.channel.tickers import Tickers, get_usdt_rates_for, to_satoshi_int
from apps.channel.pubsub_queue import publish_message_to_queue
#from apps.common.utilities.multithreading import start_new_thread

from settings import EXCHANGE_MARKETS, AWS_SNS_TOPIC_ARN
from settings import TICKERS_MINIMUM_USD_VOLUME
from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES



logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Fetch tickers every 1 minute"

    def handle(self, *args, **options):
        logger.info(f'>>> Getting ready to fetch tickers from: {", ".join(EXCHANGE_MARKETS)}')

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
        #fetch_and_process_one(exchange, usdt_rates) # for debugging
        threading.Thread(target=fetch_and_process_one, args=(exchange, usdt_rates)).start() # for production
    logger.info('\n>>> Waiting for next call of fetch_and_process_all_exchanges')


def fetch_and_process_one(exchange, usdt_rates):
    tickers = Tickers(exchange=exchange, usdt_rates=usdt_rates, minimum_volume_in_usd=TICKERS_MINIMUM_USD_VOLUME)
    tickers.run()

    # store tickers raw data in JSON format into ExchangeData
    save_to_db(tickers.tickers, exchange)

    # send message with prices/volumes to Core app
    publish_message_to_queue(message=json.dumps(tickers.symbols_info), topic_arn=AWS_SNS_TOPIC_ARN, subject='prices_volumes')

    # store price/volume data into HistoryPrice model
    save_to_history(tickers.tickers, exchange)


def save_to_db(tickers, exchange):
    timestamp = tickers[list(tickers)[0]]['timestamp']/1000 # convert from timestamp in miliseconds
    ExchangeData.objects.create(
        source=exchange,
        data=tickers, # the exact json from the ccxt
        timestamp=timestamp,
    )
    logger.debug(f">>> Saved to db: {exchange}")


def save_to_history(tickers, exchange):
    # tickers: {'BCN/BTC': {'symbol': 'BCN/BTC', 'timestamp': 1523439353595, 'datetime': '2018-04-11T09:35:54.595Z', 'high': 3.8e-07, 'low': 3.2e-07, 'bid': 3.4e-07, 'bidVolume': None, 'ask': 3.5e-07, 'askVolume': None, 'vwap': None, 'open': 3.1999999999999995e-07, 'close': 3.4e-07, 'last': 3.4e-07, 'previousClose': None, 'change': 2.000000000000002e-08, 'percentage': 6.25, 'average': 3.2999999999999996e-07, 'baseVolume': 146970152.54629916, 'quoteVolume': 51.17040999, 'info': {'id': 7, 'last': '0.00000034', 'lowestAsk': '0.00000035', 'highestBid': '0.00000034', 'percentChange': '0.06250000', 'baseVolume': '51.17040999', 'quoteVolume': '146970152.54629916', 'isFrozen': '0', 'high24hr': '0.00000038', 'low24hr': '0.00000032'}},

    source_code = next((code for code, source_text in SOURCE_CHOICES if source_text==exchange.lower()), None)

    for trading_pair, value in tickers.items():
        (transaction_currency, counter_curency_text) = trading_pair.split('/')
        if counter_curency_text in COUNTER_CURRENCIES:
            counter_currency_code = next((code for code, counter_currency in COUNTER_CURRENCY_CHOICES if counter_currency==counter_curency_text), None)
        else:
            counter_currency_code = None
        if counter_currency_code is None:
            continue # skip this counter currency
        
        HistoryPrice.objects.create(
            timestamp = value['timestamp']/1000, # convert from timestamp in miliseconds UTC
            source = source_code,
            transaction_currency = transaction_currency[0:8],
            counter_currency = counter_currency_code,
            open_price = to_satoshi_int(value['open']),
            high_price = to_satoshi_int(value['high']),
            low_price = to_satoshi_int(value['low']),
            close_price = to_satoshi_int(value['close']),
            base_volume = value['baseVolume'],
        )

    logger.debug(f">>> History saved to db for exchange: {exchange}")
