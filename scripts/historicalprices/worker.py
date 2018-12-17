import redis
import ccxt.async as ccxt
import asyncio
import sys
import json
import random

# Configure our redis client
r = redis.Redis(
	host='localhost',
	port=6379
)

exchange = sys.argv[-1]

try:
	getattr(ccxt, exchange)
except AttributeError:
	print('Specify exchange name as first argument.')
	exit()


r_todo = exchange + '-todo'
r_pending = exchange + '-pending'

# recover pending tasks
l = r.llen(r_pending)
for i in range(0, l):
	r.rpoplpush(r_pending, r_todo)

workers = []


def save(symbol, tickers):
	filename = exchange + '-' + symbol.replace('/', '-') + '.csv'
	with open(filename, "a") as f:
		for t in tickers:
			s = str(t).strip('[] ')
			f.write(s + "\n")

def request_one(i):
	task = r.rpoplpush(exchange + '-todo', exchange + '-pending')
	if task is None:
		print(exchange + ': ' + str(i) + ': No more tasks')
		return
	task = task.decode('utf-8')
	task = json.loads(task)
	asyncio.async(get_one(task, i))

async def new_proxy(proxy):
	workers.append(getattr(ccxt, exchange)({
		'aiohttp_proxy': 'http://' + proxy,
		'enableRateLimit': True,
		'rateLimit': 20000
	}))
	request_one((len(workers) -1))

async def get_one(req, i):
	global workers

	# soften IO Load
	await asyncio.sleep(random.uniform(0, 10))

	redisTask = json.dumps(req)
	symbol = req[0]
	since = req[1]
	limit = req[2]
	timeframe = req[3]
	workers = list(filter(lambda x: x, workers))
	inst = workers[i]
	if inst is None:
		print(exchange + ': ' + str(i) + ': is None')
		return

	try:
		c = await inst.fetch_ohlcv(symbol, timeframe, since, limit)
		# print(str(inst.aiohttp_proxy) + ': ' + str(c))
		save(symbol, c)
		r.lrem(exchange + '-pending', redisTask, 0)
		print(exchange + ': ' + str(i) + ': ok: ' + redisTask)
	except Exception as e: 
		print(str(i) + ': ' + str(e))
		await inst.close()
		# keep worker open but just never use again
		print(exchange + ': ' + str(i) +': failed: ' + redisTask)
		r.lrem(exchange + '-pending', redisTask)
		r.rpush(exchange + '-todo', redisTask)
		return

	request_one(i)

loop = asyncio.get_event_loop()
try:
	for proxy in r.smembers('all-proxies'):
	# for proxy in r.srandmember('all-proxies', 10):
		proxy = proxy.decode('utf-8')
		asyncio.async(new_proxy(proxy))
	loop.run_forever()
except KeyboardInterrupt:
	pass
finally:
	loop.close()
