""" Copied from
https://jakubszwajka.github.io/How-to-build-event-system-python/_
"""
from collections import defaultdict as _defaultdict
from typing import Callable as _Callable

# Uses defaultdict to not initialize a list when using a new (missing) key in the dict
subscribers = _defaultdict(list)


def subscribe(event_type: str, listener: _Callable):
    subscribers[event_type].append(listener)


def post_event(event_type: str, *args, **kwargs):
    if event_type in subscribers:
        for listener in subscribers[event_type]:
            listener(*args, **kwargs)


def clear_subscribers():
    global subscribers
    subscribers = _defaultdict(list)
