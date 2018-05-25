# import json
import logging
import os
import csv
import ast
# import re
# import io
import time

# import boto3
# import pandas as pd
from apps.channel.models import HistoryPrice
from apps.channel.models import ExchangeData

from apps.channel.helpers import source_code_from_name, counter_currency_code_from_name

from apps.channel.tickers import to_satoshi_int

from django.core.management.base import BaseCommand

from settings import BASE_DIR, COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES

# #from apps.channel.models.exchange_data import SOURCE_CHOICES
# from apps.indicator.models import Price, Volume
# from taskapp.helpers import get_source_name

# from apps.channel.incoming_queue import SqsListener

# from settings import INCOMING_SQS_QUEUE, SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES




logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Read historical data from core "channel_exchangedata" in csv format.'

    # def add_arguments(self, parser):
    #     "filename like: binance-ADA-BNB.csv"
    #     parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        ## import history from core csv
        #import_core_channel_exchangedata(filename="channel_exchangedata.csv")

        # import history from data db
        import_db_data_channel_exchangedata()


def import_db_data_channel_exchangedata():
    start_time = time.time()
    logger.info(f"Starting reading data from Data App")
    records = ExchangeData.objects.order_by('timestamp').iterator()
    #print(record.__dict__)
    #source_txt = record.source
    #print(source_txt)

    j = 0
    for record in records:
        source = source_code_from_name(record.source)
        print("ID:", record.id, "Source:", source)
        for coin, coin_value in record.data.items():
            print(f"record: {record.id}, counter: {j}, coin: {coin}")
            j += 1
            try:
                transaction_currency, counter_currency_txt  = coin.split("/")
            except: # skip
                continue
            #print(f"coin:{coin} tc:{transaction_currency} cc:{counter_currency_txt}")
            if counter_currency_txt not in COUNTER_CURRENCIES:
                print("Skipping:", coin)
                continue
            print(f"Processsing coin:{coin} tc:{transaction_currency} cc:{counter_currency_txt} from: {record.source}")

            timestamp = coin_value['timestamp']/1000
            counter_currency = counter_currency_code_from_name(counter_currency_txt)

            print(coin_value)
            # Dry run
            res = f"""
            HistoryPrice.objects.create(
                timestamp = {timestamp},
                source = {source},
                transaction_currency = {transaction_currency},
                counter_currency = {counter_currency},
                open_price = {to_satoshi_int(coin_value['open'])},
                high_price = {to_satoshi_int(coin_value['high'])},
                low_price = {to_satoshi_int(coin_value['low'])},
                close_price = {to_satoshi_int(coin_value['close'])},
                base_volume = {coin_value['baseVolume']},
                extra = 2,
            """


        #counter_currency_code = next((code for code, cc_text in COUNTER_CURRENCY_CHOICES if counter_text==cc_text), None)

        # skip None Counter currency and check if it in CC list
        #print(coin, transaction_currency, counter_currency_code)

        #break



# csv iterator
def getrow(filename):
    with open(os.path.join(BASE_DIR, filename), "r") as csvfile:
        for row in csv.reader(csvfile, delimiter=';', quotechar='"'):
            yield row

def import_core_channel_exchangedata(filename):
    logger.info(f"Starting reading historical data from: {filename}")
    iter_rows = iter(getrow(filename))
    print(f"Columns:{next(iter_rows)}")  # Skipping the column names
    for idx, row in enumerate(iter_rows):
        (_, source, data, timestamp_str) = row
        timestamp = float(timestamp_str)
        data_dict = ast.literal_eval(data)
        i = 0
        for key, value in data_dict.items():
            cc, transaction_currency = key.split("_")
            counter_currency_code = next(code for code, cc_text in COUNTER_CURRENCY_CHOICES if cc==cc_text)
            print(f"{idx} - {key} - {timestamp}")

            base_volume = float(value['baseVolume'])
            close_price = to_satoshi_int(float(value['last']))

            HistoryPrice.objects.create(
                timestamp = timestamp,
                source = source,
                transaction_currency = transaction_currency,
                counter_currency = counter_currency_code,
                close_price = close_price,
                base_volume = base_volume,
                extra = 1,
            )
            i += 1
            #break
        #break