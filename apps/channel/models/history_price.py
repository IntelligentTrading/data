from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES



class HistoryPrice(models.Model):
    # all prices in satochi integer units, divide it by 10^8 to get real values
    # timestamp, open, high, low, close, volume

    timestamp = UnixTimeStampField(null=False)                              # UTC timestamp
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)   # required, exchange code
    transaction_currency = models.CharField(max_length=8, null=False)       # required, base currency in trading pair
    counter_currency = models.SmallIntegerField(choices=COUNTER_CURRENCY_CHOICES, null=False) # required, counter currency code
    base_volume = models.FloatField(null=True)      # volume of base currency traded for last 24 hours
    open_price = models.BigIntegerField(null=True)  # opening price
    high_price = models.BigIntegerField(null=True)  # highest price
    low_price = models.BigIntegerField(null=True)   # lowest price
    close_price = models.BigIntegerField(null=True) # price of last trade (closing price for current period)
    extra = models.SmallIntegerField(null=True)     # just extra field, use it as you wish
