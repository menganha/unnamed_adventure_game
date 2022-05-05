""" Copied from
https://jakubszwajka.github.io/How-to-build-event-system-python/_
"""
from collections import defaultdict as _defaultdict
from typing import Callable as _Callable

from yazelc.event_type import EventType as _EventType

# Uses defaultdict to initialize a list when using a new (missing) key in the dict
subscribers = _defaultdict(list)


def subscribe(event_type: _EventType, listener: _Callable):
    global subscribers
    subscribers[event_type].append(listener)


def post_event(event_type: _EventType, *args, **kwargs):
    global subscribers
    if event_type in subscribers:
        for listener in subscribers[event_type]:
            listener(*args, **kwargs)


def clear_subscribers():
    global subscribers
    subscribers = _defaultdict(list)
