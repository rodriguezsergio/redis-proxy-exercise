Segment Redis Proxy
===========================

## Overview

This project uses the sanic web server (https://github.com/huge-success/sanic) as a simple read-through cache for a singular Redis instance. A python dictionary is used as the cache and a doubly linked list is used to keep track of the least recently accessed key. When a request for a non-existent key in the cache is received, the server will retrieve the associated value, if the key is present, from Redis and store it in both the cache and the linked list.

Items in the cache will remain there until either `CACHE_TTL` seconds have elapsed or the cache reaches capacity and the least recently accessed item is evicted.


## Configuration Variables

| Variable   | Default                  |
|------------|--------------------------|
| REDIS_HOST | redis                    |
| CACHE_TTL  | 15 (in seconds)          |
| CACHE_SIZE | 3                        |
| PROXY_HOST | segment                  |
| PROXY_PORT | 8080                     |
| WORKERS    | 1 (for the sanic server) |

## Code 

The `test.py` file is responsible for populating the backing Redis instance at start-up (assuming one has run `make test`). Once populated, GET requests for pre-existing keys will begin to populate the cache. In segment.py, `add_key_to_cache()` is responsible for:

- populating the python dictionary with the appropriate key and value
- adding the key to the beginning of the doubly linked list
- incrementing the linked list length by 1 as a means of tracking the current cache size
- and scheduling the removal of the key in question `CACHE_TTL` seconds in the future

Once the cache has reached capacity, the following request for a valid key not already present in the cache will cause the least recently accessed key to be removed from both the cache and linked list. Lookup of this value will occur in constant time as the linked list class keeps track of said value.

```
$ tree
.
|____docker-compose.yml - dependencies and environment variables are defined here
|____Makefile           - for running the redis proxy
|____README.md
|____segment
| |____Dockerfile       - for building the proxy and installing dependencies
| |____linkedlist.py    - for LRU cache
| |____node.py          - LRU cache depends on this
| |____segment.conf     - log rotation config
| |____segment.py       - sanic proxy
|____tests
| |____Dockerfile       - installs test dependencies and run tests against proxy
| |____test.py          - populates the redis server, populates the proxy cache, checks that keys are evicted, and ensures the TTL is adhered to
```

## Algorithmic Complexity

- Cache insertions complete in constant time. O(1)
- Cache deletions can also occur in constant time if the node is either the start or end node.
- All other nodes will be removed in O(n).

## Instructions

- To just run the proxy and redis: `make run`.
- To run the proxy, redis, and the tests: `make test`.

## Time Spent

- Basic functionality (web server proxy, docker): Between 4 and 4.5 hours
- Tests: About 1 hour
- README: About 30 minutes

Having not used `sanic` or `asyncio` before, this task took longer than expected in order to implement concurrent processing.

## Not implemented

In the interest of time, implementing a TCP Redis proxy was omitted.