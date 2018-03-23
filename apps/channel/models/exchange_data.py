from django.db import models
from django.contrib.postgres.fields import JSONField
from unixtimestampfield.fields import UnixTimeStampField



class ExchangeData(models.Model):
    source = models.CharField(max_length=128)
    data = JSONField(default="")
    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS
