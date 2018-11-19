from linkedlist import LinkedList
from sanic import Sanic
from sanic.response import json, text
from sanic.exceptions import abort
import asyncio
import aioredis
import os
import logging
app = Sanic()


async def add_key_to_cache(key, val):
    app.lru.add_node(key)
    app.cache[key] = val.decode('utf-8')
    asyncio.ensure_future(remove_expired_key(key))


async def remove_expired_key(key):
    await asyncio.sleep(int(os.environ['CACHE_TTL']))
    logging.info('Key, {}, has expired. Removing it from the cache.'.format(key))

    app.cache.pop(key, None)
    app.lru.remove_node(key)
    logging.info('Cache state: {}.'.format(app.cache))


async def evict_lru_key():
    lru_key = app.lru.end.get_data()
    logging.info('Evicting least recently used key: {}.'.format(lru_key))

    app.lru.remove_node(lru_key)
    app.cache.pop(lru_key, None)
    logging.info('Cache state: {}.'.format(app.cache))


@app.listener('before_server_start')
async def start_up(app, loop):
    app.lru = LinkedList()
    app.cache = {}
    app.redis = await aioredis.create_pool(
        address=(os.environ['REDIS_HOST'], 6379),
        minsize=5,
        maxsize=10,
        loop=loop
    )


@app.listener('after_server_stop')
async def shut_down(app, loop):
    app.redis.close()
    await app.redis.wait_closed()


@app.route('/key/<key>')
async def get_entry(request, key):
    logging.info('Looking up key: {}.'.format(key))

    if key in app.cache:
        logging.info('Value, {}, for key, {}, found in app.cache.'.format(app.cache[key], key))
        app.lru.remove_node(key)
        app.lru.add_node(key)
        return json({
            'value': int(app.cache[key]),
            'fromCache': True
        })

    async with app.redis.get() as redis:
        val = await redis.execute('get', key)

    if val is None:
        return abort(404)

    if app.lru.get_length() == int(os.environ['CACHE_SIZE']):
        await evict_lru_key()

    await add_key_to_cache(key, val)

    logging.info('Cache state: {}.'.format(app.cache))

    return json({
        'value': int(val.decode('utf-8')),
        'fromCache': False
    })

if __name__ == "__main__":
    # write logs to disk
    logFormat='%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormat, filename='logs/segment.log', level=logging.DEBUG)
    logger = logging.getLogger()

    # configure console logging to match
    consoleLogger = logging.StreamHandler()
    consoleLogger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(logFormat)
    consoleLogger.setFormatter(formatter)

    logger.addHandler(consoleLogger)

    app.run(host='0.0.0.0', port=os.environ['PROXY_PORT'], workers=int(os.environ['WORKERS']))
