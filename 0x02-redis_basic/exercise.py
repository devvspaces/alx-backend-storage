#!/usr/bin/env python3
"""
Cache store
"""

from typing import Any, Callable, Type, Union
from uuid import uuid4
from redis import Redis
from functools import wraps


def count_calls(fn: Callable) -> Callable:
    """Decorator to count the number of calls to a function.
    """
    @wraps(fn)
    def wrapper(self: Type['Cache'], *args, **kwargs) -> Any:
        """Wrapper function to count the number of calls to a function.

        :param self: The Cache instance.
        :type self: Cache
        :return: The result of the function.
        :rtype: Any
        """
        self._redis.incr(fn.__qualname__)
        return fn(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.

    :param method: The method to decorate.
    :type method: Callable
    :return: The wrapper function.
    :rtype: Callable
    """
    @wraps(method)
    def wrapper(self: Type['Cache'], *args, **kwargs) -> Any:
        """Wrapper function to store the history
        of inputs and outputs for a function.

        :param self: The Cache instance.
        :type self: Cache
        :return: The result of the function.
        :rtype: Any
        """
        if isinstance(self._redis, Redis):
            value = str(tuple([i.decode('utf-8') if type(i) == bytes else i for i in args]))
            self._redis.rpush(f'{method.__qualname__}:inputs', value)
        result = method(self, *args, **kwargs)
        self._redis.rpush(f'{method.__qualname__}:outputs', result)
        return result
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a function.

    :param method: The method to replay.
    :type method: Callable
    """
    method_name = method.__qualname__
    inputs = method_name + ':inputs'
    outputs = method_name + ':outputs'
    cache = method.__self__
    if isinstance(cache._redis, Redis):
        count = cache.get_str(method_name)
        print(f'{method_name} was called {count} times:')
        inputs_list = cache._redis.lrange(inputs, 0, -1)
        outputs_list = cache._redis.lrange(outputs, 0, -1)
        for i, o in zip(inputs_list, outputs_list):
            print(f'{method_name}(*{i.decode("utf-8")}) -> {o.decode("utf-8")}')


class Cache:
    """Cache class to store data in Redis.
    """

    def __init__(self) -> None:
        """Initialize the Cache instance.
        """
        self._redis = Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the input data in Redis using a random key.

        :param data: The data to store.
        :type data: Union[str, bytes, int, float]
        """
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    @count_calls
    def get(
        self, key: str, fn: Callable = None
    ) -> Union[str, bytes, int, float]:
        """
        Get the data stored in Redis using the input key.

        :param key: The key to retrieve.
        :type key: str
        :param fn: The function to apply to the data.
        :type fn: callable
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    @count_calls
    def get_str(self, key: str) -> str:
        """Retrieves a string value from a Redis data storage.

        :param key: key to retrieve
        :type key: str
        :return: string value
        :rtype: str
        """
        return self.get(key, lambda x: x.decode('utf-8'))

    @count_calls
    def get_int(self, key: str) -> int:
        """Retrieves an integer value from a Redis data storage.

        :param key: key to retrieve
        :type key: str
        :return: integer value
        :rtype: int
        """
        return self.get(key, lambda x: int(x))
