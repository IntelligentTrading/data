from django.db import models
from django.contrib.postgres.fields import JSONField
from unixtimestampfield.fields import UnixTimeStampField


(POLONIEX, BITTREX, BINANCE, BITFINEX) = list(range(4))
SOURCE_CHOICES = (
    (POLONIEX, 'poloniex'),
    (BITTREX, 'bittrex'),
    (BINANCE, 'binance'),
    (BITFINEX, 'bitfinex')
)


class ExchangeData(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    data = JSONField(default="")
    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS
