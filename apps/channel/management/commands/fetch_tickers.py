import json
import logging
import sys
import time
import threading

import schedule

import ccxt

from django.core.management.base import BaseCommand

from apps.channel.models import ExchangeData

from apps.channel.tickers import Tickers, get_usdt_rates_for, to_satoshi_int
from apps.channel.pubsub_queue import publish_message_to_queue

from settings import EXCHANGE_MARKETS, AWS_SNS_TOPIC_ARN
from settings import TICKERS_MINIMUM_USD_VOLUME
from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES



logger = logging.getLogger(__name__)

class Command(BaseCommand): # fetch_tickers
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


def save_to_db(tickers, exchange):
    timestamp = tickers[list(tickers)[0]]['timestamp']/1000 # convert from timestamp in miliseconds
    ExchangeData.objects.create(
        source=exchange,
        data=tickers, # the exact json from the ccxt
        timestamp=timestamp,
    )
    logger.debug(f">>> Saved to db: {exchange}")
