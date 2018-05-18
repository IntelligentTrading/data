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
    help = "Search for missing historical data and request all from Poloniex"

    def handle(self, *args, **options):
        logger.info("Getting ready to fill in missing Poloniex data...")
        # search for missing entries in the database
        # create a list of desired timestamps for datapoints
        # for each timestamp, request data from Poloniex
        # save data in database at that timestamp
