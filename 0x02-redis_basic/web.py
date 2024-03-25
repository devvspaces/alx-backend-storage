#!/usr/bin/env python3

"""Implementing an expiring web cache and tracker
"""

from typing import Callable
from redis import Redis
import requests
from functools import wraps

conn = Redis()


def data_cacher(method: Callable) -> Callable:
    """Decorator to cache the output of a method.
    """
    @wraps(method)
    def invoker(url) -> str:
        """Invokes the given method after caching its output.
        """
        conn.incr(f'count:{url}')
        result = conn.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        conn.set(f'count:{url}', 0)
        conn.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    """
    Get the content of a web page.

    :param url: The URL of the page.
    :type url: str
    :return: The content of the page.
    :rtype: str
    """
    return requests.get(url).text
