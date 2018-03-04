import json
import logging
import schedule
import time
import ccxt

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import BITFINEX

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Bitfinex every 1 minute"

    def handle(self, *args, **options):
        logger.info("Getting ready to poll Bitfinex...")
        schedule.every(1).minutes.do(poll_latest_bitfinex_data)

        keep_going=True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info("Bitfinex polling shut down.")
                keep_going = False


def poll_latest_bitfinex_data():
    try:
        logger.info("polling for Bitfinex data...")
        bitfinex = ccxt.bitfinex2()
        tickers = bitfinex.fetch_tickers()
        timestamp = float(tickers['BTC/USD']['timestamp']) / 1000

        bitfinex_data_point = ExchangeData.objects.create(
            source=BITFINEX,
            data=tickers,
            timestamp=timestamp
        )
        logger.info("Saving Bitfinex data...")

    except RequestException:
        return 'Error to collect data from Bitfinex'
