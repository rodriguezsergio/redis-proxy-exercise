import asyncio
import aiohttp
import aioredis
import os


async def populate_redis():
    redis = await aioredis.create_pool(
        address=(os.environ['REDIS_HOST'], 6379),
        minsize=5,
        maxsize=10,
        loop=asyncio.get_event_loop()
    )
    async with redis.get() as redis:
        for idx, i in enumerate('abcdefghijkl'):
            await redis.execute('set', i, idx+1)
    redis.close()
    await redis.wait_closed()
    print('Redis prepopulated with data.')


async def populate_cache(session, BASE_URL):
    for idx, key in enumerate('abcdefghijkl'):
        resp = await session.get(BASE_URL + key)
        json = await resp.json()
        async with resp:
            assert resp.status == 200
            assert json['value'] == idx + 1
    print('Cache is populated and values match expected output.')


async def check_for_evicted_values(session, BASE_URL):
    for idx, key in enumerate('abc'):
        resp = await session.get(BASE_URL + key)
        json = await resp.json()
        async with resp:
            assert resp.status == 200
            assert json['fromCache'] == False
    print('Least recently used keys have been evicted.')


async def check_for_cached_values(session, BASE_URL, in_cache=True):
    if not in_cache:
        await asyncio.sleep(int(os.environ['CACHE_TTL']))
    for idx, key in enumerate('abc'):
        resp = await session.get(BASE_URL + key)
        json = await resp.json()
        async with resp:
            assert resp.status == 200
            assert json['fromCache'] == in_cache
    if in_cache:
        print('Values have been cached.') 
    else:
        print('Cache values have expired.')


async def main():
    await asyncio.wait_for(populate_redis(), 10)
    session = aiohttp.ClientSession()
    BASE_URL = 'http://{}:{}/key/'.format(os.environ['PROXY_HOST'], os.environ['PROXY_PORT'])
    await populate_cache(session, BASE_URL)
    await check_for_evicted_values(session, BASE_URL)
    await check_for_cached_values(session, BASE_URL)
    await check_for_cached_values(session, BASE_URL, False)
    await session.close()
    print('All tests passed.')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
