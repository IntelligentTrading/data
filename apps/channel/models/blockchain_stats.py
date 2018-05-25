from django.db import models
from unixtimestampfield.fields import UnixTimeStampField


# {
#   "market_price_usd": 610.036975,
#   "hash_rate": 1.8410989266292908E9,
#   "total_fees_btc": 6073543165,
#   "n_btc_mined": 205000000000,
#   "n_tx": 233805,
#   "n_blocks_mined": 164,
#   "minutes_between_blocks": 8.2577,
#   "totalbc": 1587622500000000,
#   "n_blocks_total": 430098,
#   "estimated_transaction_volume_usd": 1.2342976868108143E8,
#   "blocks_size": 117490685,
#   "miners_revenue_usd": 1287626.6577490852,
#   "nextretarget": 431423,
#   "difficulty": 225832872179,
#   "estimated_btc_sent": 20233161880242,
#   "miners_revenue_btc": 2110,
#   "total_btc_sent": 184646388663542,
#   "trade_volume_btc": 21597.09997288,
#   "trade_volume_usd": 1.3175029536228297E7,
#   "timestamp": 1474035340000
# }

class BlockchainStats(models.Model):
    timestamp = UnixTimeStampField(null=False)

    market_price_usd = models.FloatField(null=True)
    hash_rate = models.FloatField(null=True)
    total_fees_btc = models.BigIntegerField(null=True)
    n_btc_mined = models.BigIntegerField(null=True)
    n_tx = models.IntegerField(null=True)
    n_blocks_mined = models.IntegerField(null=True)
    minutes_between_blocks = models.FloatField(null=True)
    totalbc = models.BigIntegerField(null=True)
    n_blocks_total = models.IntegerField(null=True)
    estimated_transaction_volume_usd = models.FloatField(null=True)
    blocks_size = models.BigIntegerField(null=True)
    miners_revenue_usd = models.FloatField(null=True)
    nextretarget = models.IntegerField(null=True)
    difficulty = models.BigIntegerField(null=True)
    estimated_btc_sent = models.BigIntegerField(null=True)
    miners_revenue_btc = models.IntegerField(null=True)
    total_btc_sent = models.BigIntegerField(null=True)
    trade_volume_btc = models.FloatField(null=True)
    trade_volume_usd = models.FloatField(null=True)
