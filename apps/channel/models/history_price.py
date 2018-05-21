import logging

from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES



logger = logging.getLogger(__name__)

class HistoryPrice(models.Model):
#     # all prices in satochi integer units, divide it by 10^8 to get real values
#     # timestamp, open, high, low, close, volume
    timestamp = UnixTimeStampField(null=False)                              # UTC timestamp
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)   # required
    transaction_currency = models.CharField(max_length=8, null=False)       # required
    counter_currency = models.SmallIntegerField(choices=COUNTER_CURRENCY_CHOICES, null=False) # required
    base_volume = models.FloatField(null=True)
    open_price = models.BigIntegerField(null=True)
    high_price = models.BigIntegerField(null=True)
    low_price = models.BigIntegerField(null=True)
    close_price = models.BigIntegerField(null=True)
    extra = models.SmallIntegerField(null=True)     # just extra field, use it as you wish
