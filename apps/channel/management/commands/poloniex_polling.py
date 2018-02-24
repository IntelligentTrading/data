import json
import logging
import schedule
import time

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Poloniex every 1 minute"

    def handle(self, *args, **options):
        logger.info("Getting ready to poll Poloniex...")
        schedule.every(1).minutes.do(pull_poloniex_data)
        keep_going=True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info("Poloniex polling shut down.")
                keep_going = False


def pull_poloniex_data():
    try:
        logger.info("pulling Poloniex data...")
        req = get('https://poloniex.com/public?command=returnTicker')

        poloniex_data_point = ExchangeData.objects.create(
            source=POLONIEX,
            data=req.json(), # the exact json from the request data
            timestamp=time.time() # now
        )
        logger.info("Saving Poloniex price, volume data...")

    except RequestException:
        return 'Error to collect data from Poloniex'
