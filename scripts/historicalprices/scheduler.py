# python scheduler.py binance 1483228800 'ETH/BTC' 500 60 1m
import redis

import ccxt
import asyncio
import time
from datetime import date
import random
import sys
import json

# Configure our redis client
r = redis.Redis(
	host='localhost',
	port=6379
)

print(str(sys.argv))

timestamp = int(sys.argv[2])
exchange = sys.argv[1]
symbol = sys.argv[3].strip()
limit = int(sys.argv[4])
secondsPerTick = int(sys.argv[5])
timeframe = sys.argv[6]

try:
	ccxt_exchange = getattr(ccxt, exchange)()
except AttributeError:
	print('Specify exchange name as first argument.')
	exit()

try:
	markets = ccxt_exchange.fetch_markets()
	if not any(x for x in markets if x['symbol'] == symbol):
		print('symbol not available: ' + str(symbol))
		print('Available symbols: ' + str(markets))
		exit()
except:
	print('Cant verify if symbol exists, asume it is correct: ' + symbol)


multiplier = 1000

while (timestamp + 1) < time.time():
	task = [symbol, (timestamp * multiplier), limit, timeframe]
	r.lpush(exchange + '-todo', json.dumps(task))
	timestamp = timestamp + (limit * secondsPerTick)
