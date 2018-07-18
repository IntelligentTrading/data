""" lists pair names, lowest volume first """

import ccxt
import sys


exchange = sys.argv[-1]

try:
	ex = getattr(ccxt, exchange)()
except AttributeError:
	print('Specify exchange name as first argument.')
	exit()

tickers = ex.fetch_tickers()

# 'ETH/BTC': 102923 (USD), ... 
tickers_usd = {}

for symbol, ticker in tickers.items():
	quoteCurrency = symbol.split('/')[1]
	if quoteCurrency != 'USD' and quoteCurrency != 'USDT':
		quoteUsd = quoteCurrency + '/USD'
		try:
			quotePair = tickers[quoteUsd]
			quotePrice = quotePair['last']
		except KeyError:
			try:
				quoteUsd = quoteCurrency + '/USDT'
				quotePair = tickers[quoteUsd]
				quotePrice = quotePair['last']
			except KeyError:
				quotePrice = 0
	else:
		quotePrice = 1

	thisPrice = quotePrice * ticker['last']
	volumeUsd = thisPrice * ticker['baseVolume']
	tickers_usd[symbol] = volumeUsd

tickers_sorted = sorted(tickers_usd, key=tickers_usd.get, reverse=True)
for x in tickers_sorted:
	print(x)