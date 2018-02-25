import json
import logging
import schedule
import time

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import BINANCE

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Binance every 1 minute"

    def handle(self, *args, **options):
        logger.info("Getting ready to poll Binance...")
        schedule.every(1).minutes.do(poll_latest_binance_data)

        keep_going = True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info("Binance polling shut down.")
                keep_going = False


def poll_latest_binance_data():
    try:
        logger.info("polling for Binance data...")
        req = get('https://api.binance.com/api/v1/ticker/24hr')

        binance_data_point = ExchangeData.objects.create(
            source=BINANCE,
            data=req.json(),
            timestamp=time.time()
        )
        logger.info("Saving Binance data...")

    except RequestException:
        return 'Error to collect data from Binance'
