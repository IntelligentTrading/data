import ccxt # https://github.com/ccxt/ccxt/tree/master/python



def fetch_tickers_from(exchange_id):
    exchange = getattr(ccxt, exchange_id)()
    tickers = exchange.fetch_tickers()
    return tickers
    

if __name__ == '__main__':
    ticks = fetch_tickers_from('poloniex')
    print(ticks)