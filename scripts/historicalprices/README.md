Cryptocurrency historical price proxy client
========================================

This script can be used to download historical price data from cryptocurrency exchanges using the [ccxt](https://github.com/ccxt/ccxt) library using proxies found through [ProxyBroker](https://github.com/constverum/ProxyBroker). 

### Problem
Exchanges give away historical price data, but their APIs are heavily rate limited. To download a few months worth of data for more than a handful of coins will take forever. 

### Solution
Proxies. Lots of them.

1. Find working proxies using ProxyBroker and save list to redis
2. Queue all API requests in redis
3. Execute as many requests as possible in parallel (using redis to keep track of failed requests to queue for retry)
4. Sort results

### Requirements
- [moreutils](https://rentes.github.io/unix/utilities/2015/07/27/moreutils-package/) (Install using your package manager)
- Python 3.6.0 (recommended to use [pyenv](https://github.com/pyenv/pyenv))
- pip modules [`proxybroker`](https://github.com/constverum/ProxyBroker), [`ccxt`](https://github.com/ccxt/ccxt), `redis`
- redis _or_ docker

*Setup Python + packages on Ubuntu:*

```sh
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev moreutils

curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

append to `.bashrc`:

```sh
export PATH="/root/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

```sh
source .bashrc

pyenv install 3.6.0
pyenv local 3.6.0

pip install --upgrade pip
pip install ccxt redis proxybroker/
```


### Usage
Note: Exchange names are according to ccxt.

0. Start redis
```sh
docker run -p 6379:6379 redis
```
1. Get a list of pairs you want to download. You can use `pairs-by-volume.py` for this (which will list all exchange pairs based on 24h volume).
```sh
python pairs-by-volume.py bitfinex2 > bitfinex-pairs.txt
```
2. Queue API calls. The `scheduler.py` script will queue all calls to download data of 1 pair on 1 exchange. We'll invoke it for every pair collected in step 1:
```sh
while read p; do
	python scheduler.py bitfinex2       1483228800         "$p"     1000                                            60                        1m
	#                    exchange,      start timestamp,   pair,     how many candles per request the API returns, candle length in seconds, candle length as ccxt duration string
	#                                   end = now
done < bitfinex-pairs.txt
```
3. Get proxies. Let this run for ~10 minutes before jumping to the next step.
```sh
python proxies-indefinitely.py
```
4. Execute the API requests. One worker instance takes care of one exchange, so if you want to download multiple exchanges at once you'll need to start this script multiple times. `Worker.py` saves state to redis, if it crashes it will pick up just were it left off. It's finished when you see a bunch of `No more tasks` lines in the console. Just to make sure you should invoke this script again afterwards, don't really have a status indicator yet.
```sh
python worker.py bitfinex2
```
5. Now you should have a bunch of files like `bitfinex2-ETH-USD.csv` in the folder you invoked the `worker.py` script. Sort and dedup:
```
mkdir done
cp bitfinex2-*.csv done
cd done
for i in *; do cat "$i" | sort | uniq | sponge "$i"; done
```


### More details
Redis queues are namespaced by exchange. `scheduler.py` will will the `exchange-todo` queue, `worker.py` will move tasks to the `exchange-pending` queue and then remove from the list once successfully executed. `worker.py` runs 1 "thread" for every proxy found. CCXT will issue 1 request every 20 seconds. To see how far the script has come, check the length of the `exchange-todo` queue using redis-cli.


### Scheduler.py params for popular exchanges
| exchange  | smallest candle length | candles per API request | oldest data |
| -------   | --------------------   | ----------------------- | ----------- |
| binance   |    1m                  |    500                  |             |
| bitfinex2 |                        |   1000                  |             |
| hitbtc2   |                        |      1000               |             |
| gdax      |       1m               |        300              |             |
| kucoin    |       30m              | 30000                   | 1498921487  |
| poloniex  |       5m               | 30000                   |             |

