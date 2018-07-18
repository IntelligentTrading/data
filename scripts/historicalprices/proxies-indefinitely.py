import asyncio
import redis
from proxybroker import Broker

r = redis.Redis(
	host='localhost',
	port=6379
)


async def show(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        s = '%s:%d' % (proxy.host, proxy.port)
        length = r.scard('all-proxies')
        r.sadd('all-proxies', s)
        new_length = r.scard('all-proxies')
        if length != new_length:
        	r.publish('proxies', s)
        	print('Found proxy: %s' % s)
        else:
        	print('Old proxy found: %s' % s)
        

proxies = asyncio.Queue()
broker = Broker(proxies)
tasks = asyncio.gather(
    broker.find(types=['HTTP', 'HTTPS']),
    show(proxies))

loop = asyncio.get_event_loop()
loop.run_until_complete(tasks)