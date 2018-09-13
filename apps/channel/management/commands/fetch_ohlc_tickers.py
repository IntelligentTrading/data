import json
import logging
import time

import requests
import schedule
from django.core.management.base import BaseCommand

from apps.channel.pubsub_queue import publish_message_to_queue
from apps.channel.tickers import Tickers, get_usdt_rates_for
from apps.common.utilities.multithreading import start_new_thread
from settings import EXCHANGE_MARKETS, AWS_SNS_TOPIC_ARN, SNS_PRICES_BATCH_SIZE, ITF_API, ITF_API_KEY, DEBUG
from settings import TICKERS_MINIMUM_USD_VOLUME

logger = logging.getLogger(__name__)

class Command(BaseCommand):  # fetch_ohlc_tickers
    help = "Fetch tickers every 1 minute"

    def handle(self, *args, **options):
        logger.info(f'>>> Getting ready to fetch ohlc tickers from: {", ".join(EXCHANGE_MARKETS)}')

        usdt_rates = get_usdt_rates_for('BTC', 'ETH')

        #fetch_and_process_all_exchanges(usdt_rates); return # one iteration for debug only

        schedule.every(1).minutes.do(fetch_and_process_all_exchanges, usdt_rates)
        if DEBUG:
            fetch_and_process_all_exchanges(usdt_rates) # and go now too!

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
        fetch_and_process_one(exchange, usdt_rates)
    logger.info('\n>>> Waiting for next call of fetch_and_process_all_exchanges')


def fetch_and_process_one(exchange, usdt_rates):
    tickers = Tickers(exchange=exchange, usdt_rates=usdt_rates, minimum_volume_in_usd=TICKERS_MINIMUM_USD_VOLUME)
    tickers.run()

    send_ohlc_data_to_api(tickers)
    send_ohlc_data_to_queue(tickers)


@start_new_thread
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


@start_new_thread
def send_ohlc_data_to_api(tickers_object):
    for symbol, symbol_info in tickers_object.tickers.items():

        if not symbol.count('/') == 1: # check format is like "ETH/BTC"
            # skip malformed currency pairs
            logger.debug(f'Skipping symbol: {symbol}')
            continue

        if tickers_object.exchange != "binance": # ignore other exchanges for now
            logger.debug(f'Skipping non-binance symbol: {symbol}')
            continue

        if symbol.endswith("ETH"): # skip ETH counter currency tickers
            logger.debug(f'Skipping ETH symbol: {symbol}')
            continue

        if tickers_object._symbol_allowed(symbol_info=symbol_info,
                                          usdt_rates=tickers_object.usdt_rates,
                                          minimum_volume_in_usd=tickers_object.minimum_volume_in_usd):

            ticker = symbol.replace("/","_")
            headers = {'API-KEY': ITF_API_KEY}
            r = requests.put(f'{ITF_API}/v3/historical_data/{ticker}', headers=headers,
                             json={
                                 'exchange': tickers_object.exchange,
                                 'ticker': symbol_info['symbol'],
                                 'timestamp': int(symbol_info['timestamp'] / 1000),  # milliseconds -> sec
                                 'open_price': symbol_info['open'],
                                 'high_price': symbol_info['high'],
                                 'low_price': symbol_info['low'],
                                 'close_price': symbol_info['close'],
                                 'close_volume': symbol_info['baseVolume'],
                             })

            try:
                logger.debug(r.url)
                logger.debug(str(r.json()))
            except:
                pass
