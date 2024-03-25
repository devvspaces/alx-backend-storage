#!/usr/bin/env python3

"""Implementing an expiring web cache and tracker
"""

from typing import Callable
from redis import Redis
import requests
from functools import wraps

conn = Redis()


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of calls to a function.

    :param method: The method to decorate.
    :type method: Callable
    :return: The wrapper function.
    :rtype: Callable
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function to count the number of calls to a function.

        :param url: The URL of the page.
        :type url: str
        :return: The content of the page.
        :rtype: str
        """
        conn.incr(f"count:{url}")
        return method(url)
    return wrapper


def cache(time: int) -> Callable:
    """Decorator to cache the result of a function.

    :param time: The time in seconds to store the result.
    :type time: int
    :return: The decorator function.
    :rtype: Callable
    """
    def cache_url(method: Callable) -> Callable:
        """Decorator to cache the result of a function.
        """
        @wraps(method)
        def wrapper(url: str) -> str:
            """Wrapper function to cache the result of a function.
            """
            key = f"cache:{url}"
            page = conn.get(key)
            if not page:
                page = method(url)
                conn.setex(key, time, page)
            return page
        return wrapper
    return cache_url


@cache(10)
@count_calls
def get_page(url: str) -> str:
    """
    Get the content of a web page.

    :param url: The URL of the page.
    :type url: str
    :return: The content of the page.
    :rtype: str
    """
    return requests.get(url).text
