
# https://api.blockchain.info/stats
# Docs: https://blockchain.info/api/charts_api
import logging
import time

import requests
import schedule

from django.core.management.base import BaseCommand

from apps.channel.models import BlockchainStats



logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Fetch blockchain stats every 1 minute"

    def handle(self, *args, **options):
        logger.info(f'>>> Ready to fetch blockchain stats')
        # fetch_blockchain_stats(); return

        schedule.every(5).minutes.do(fetch_and_save_blockchain_stats)

        keep_going = True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(30)
            except Exception as e:
                logger.error(e)
                logger.info(">>> Fetching blockchain stats shut down")
                keep_going = False


def fetch_and_save_blockchain_stats():
    logger.debug("Fetching blockchain stats")
    
    req = requests.get('https://api.blockchain.info/stats')
    data = req.json()

    BlockchainStats.objects.create(
        timestamp           = data['timestamp']/1000, # convert from timestamp in miliseconds UTC
        market_price_usd    = data['market_price_usd'],
        hash_rate           = data['hash_rate'],
        total_fees_btc      = data['total_fees_btc'],
        n_btc_mined         = data['n_btc_mined'],
        n_tx                = data['n_tx'],
        n_blocks_mined      = data['n_blocks_mined'],
        minutes_between_blocks = data['minutes_between_blocks'],
        totalbc             = data['totalbc'],
        n_blocks_total      = data['n_blocks_total'],
        estimated_transaction_volume_usd = data['estimated_transaction_volume_usd'],
        blocks_size         = data['blocks_size'],
        miners_revenue_usd  = data['miners_revenue_usd'],
        nextretarget        = data['nextretarget'],
        difficulty          = data['difficulty'],
        estimated_btc_sent  = data['estimated_btc_sent'],
        miners_revenue_btc  = data['miners_revenue_btc'],
        total_btc_sent      = data['total_btc_sent'],
        trade_volume_btc    = data['trade_volume_btc'],
        trade_volume_usd    = data['trade_volume_usd'],
    )
    logger.debug("Blockchain stats saved")

