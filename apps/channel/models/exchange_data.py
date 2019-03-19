from django.db import models
from django.contrib.postgres.fields import JSONField
from unixtimestampfield.fields import UnixTimeStampField

from settings import SOURCE_CHOICES

(POLONIEX, BINANCE, KUCOIN) = list(range(3))
SOURCE_CHOICES = (
    (POLONIEX, 'poloniex'),
    (BINANCE, 'binance'),
    (KUCOIN, 'kucoin'),
)

class ExchangeData(models.Model):
    source = models.CharField(max_length=128)
    data = JSONField(default="")
    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES
    
    # MODEL FUNCTIONS

