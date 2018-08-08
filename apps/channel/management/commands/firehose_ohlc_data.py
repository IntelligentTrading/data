import logging

import requests
from django.core.management.base import BaseCommand

from apps.channel.models import ExchangeData
from apps.channel.tickers import Tickers
from settings import ITF_API, ITF_API_KEY

logger = logging.getLogger(__name__)

class Command(BaseCommand): # firehose_ohlc_data
    help = "=== THE FIREHOSE ==="

    def handle(self, *args, **options):
        logger.info(f'Getting ready to push entire history of ohlc tickers')

        for exchange_data_object in ExchangeData.objects.order_by('timestamp')[0:65000]:
            tickers_object = Tickers(exchange=exchange_data_object.source)
            tickers_object.tickers = exchange_data_object.data

            for symbol, symbol_info in tickers_object.tickers.items():

                if not symbol.count('/') == 1: # check format is like "ETH/BTC"
                    logger.debug(f'Skipping symbol: {symbol}')
                    continue # skip malformed currency pairs

                if not tickers_object._symbol_allowed(symbol_info=symbol_info):
                    logger.debug(f'Skipping symbol: {symbol}')
                    continue

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

                if not "success" in r.json():
                    logger.debug(str(r.json()))
