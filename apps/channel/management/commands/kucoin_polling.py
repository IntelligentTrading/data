import json
import logging
import schedule
import time

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import KUCOIN

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from KuCoin every 1 minute"

    def handle(self, *args, **options):
        logger.info("Getting ready to poll KuCoin...")
        schedule.every(1).minutes.do(poll_latest_kucoin_data)

        keep_going=True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info("Kucoin polling shut down.")
                keep_going = False


def poll_latest_kucoin_data():
    try:
        logger.info("polling for Kucoin data...")
        req = get('https://api.kucoin.com/api/v1/market/allTickers')

        kucoin_data_point = ExchangeData.objects.create(
            source=KUCOIN,
            data=req.json(), # the exact json from the request data
            timestamp=time.time() # now
        )
        logger.info("Saving Kucoin data...")

    except RequestException:
        return 'Error to collect data from Kucoin'
