import logging
import time
import datetime
import requests
from django.core.management.base import BaseCommand

from apps.channel.models import ExchangeData
from apps.channel.tickers import Tickers
from settings import ITF_API, ITF_API_KEY

logger = logging.getLogger(__name__)


class Command(BaseCommand):  # firehose_ohlc_data
    help = "=== THE FIREHOSE ===" + """
                                               )
  ,%,                                     ) _(___[]_
  %%%,&&&,                     ,%%,      (;`       /\
  %Y/%&&&&                     %%%%   ___/_____)__/ _\__     ,%%,
^^^||^&\Y&^^^^^^^^^^^^^^^^^^^^^%Y/%^^/ (_()   (  | /____/\^^^%%%%^^
  `    || _,..=xxxxxxxxxxxx,    ||   |(' |LI (.)I| | LI ||   %\Y%
 -=      /L_Y.-#########`,-n-. `    @'---|__||___|_|____||_   ||
___-=___.--'[========]|L]J: []\ __________@//@___________) )______
-= _ _ _ |/ _ ''_ " " ||[ -_ 4 |  _  _  _  _  _  _  _  _  _  _  _
        '-(_)-(_)----'v'-(_)--'
jgs-----------------------------------------------------------------
    """

    def handle(self, *args, **options):
        logger.info(f'Getting ready to push entire history of ohlc tickers')

        timestamp = jan_1_2017 = 1483228800
        today = int(time.time())
        increment = 86400  # seconds in 1 day

        while timestamp < today:
            timestamp += increment
            logger.info("Running ... " + datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))

            for exchange_data_object in ExchangeData.objects.order_by('timestamp').filter(
                    timestamp__gt=(timestamp - increment), timestamp__lte=timestamp
            ):
                tickers_object = Tickers(exchange=exchange_data_object.source)
                tickers_object.tickers = exchange_data_object.data

                for symbol, symbol_info in tickers_object.tickers.items():

                    if not symbol.count('/') == 1:  # check format is like "ETH/BTC"
                        # logger.debug(f'Skipping symbol: {symbol}')
                        continue  # skip malformed currency pairs

                    if not tickers_object._symbol_allowed(symbol_info=symbol_info):
                        # logger.debug(f'Skipping symbol: {symbol}')
                        continue

                    if tickers_object.exchange != "binance":  # ignore other exchanges for now
                        logger.debug(f'Skipping non-binance symbol: {symbol}')
                        continue

                    if symbol.endswith("ETH"):  # skip ETH counter currency tickers
                        logger.debug(f'Skipping ETH symbol: {symbol}')
                        continue

                    ticker = symbol.replace("/", "_")
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

                    if not "success" in r.json():
                        logger.debug(str(r.json()))
