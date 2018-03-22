import json
import logging
import time
import schedule

import ccxt

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData

from settings import EXCHANGE_MARKETS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch tickers every 1 minute"

    def handle(self, *args, **options):
        logger.info("Getting ready to fetch tickers from exchanges")

        # FIXME choose better scheduling later
        schedule.every(1).minutes.do(fetch_and_process_all)

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

        symbols_info = process_tickers(tickers)
        send_to_queue(symbols_info)

def fetch_tickers_from(exchange_id):
    # we use ccxt: https://github.com/ccxt/ccxt/tree/master/python
    exchange = getattr(ccxt, exchange_id)()
    tickers = exchange.fetch_tickers()
    return tickers

def process_tickers(tickers):
    # Processsing
    print("Processed:", len(tickers))
    return tickers

def send_to_queue(symbols_info):
    print("Sent to queue:", len(symbols_info), "messages")

def save_to_db(tickers, exchange_id):
    timestamp = tickers[list(tickers)[0]]['timestamp']/1000 # convert from timestamp in miliseconds
    ExchangeData.objects.create(
        source=exchange_id,
        data=tickers, # the exact json from the request data
        timestamp=timestamp,
    )
    logger.info(f"Saved to db: {exchange_id}")



#         schedule.every(1).minutes.do(poll_latest_poloniex_data)

#         keep_going=True
#         while keep_going:
#             try:
#                 schedule.run_pending()
#                 time.sleep(1)
#             except Exception as e:
#                 logger.debug(str(e))
#                 logger.info("Poloniex polling shut down.")
#                 keep_going = False


# def poll_latest_poloniex_data():
#     try:
#         logger.info("polling for Poloniex data...")
#         req = get('https://poloniex.com/public?command=returnTicker')

#         poloniex_data_point = ExchangeData.objects.create(
#             source=POLONIEX,
#             data=req.json(), # the exact json from the request data
#             timestamp=time.time() # now
#         )
#         logger.info("Saving Poloniex data...")

#     except RequestException:
#         return 'Error to collect data from Poloniex'
