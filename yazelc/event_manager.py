from collections import defaultdict
from typing import Callable

from yazelc.event_type import EventType


class EventManager:
    """ Copied from
    https://jakubszwajka.github.io/How-to-build-event-system-python/_
    """

    def __init__(self):
        # Uses defaultdict to initialize a list when using a new (missing) key in the dict
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: EventType, listener: Callable):
        self.subscribers[event_type].append(listener)

    def post_event(self, event_type: EventType, *args, **kwargs):
        if event_type in self.subscribers:
            for listener in self.subscribers[event_type]:
                listener(*args, **kwargs)

    def clear(self):
        self.subscribers = defaultdict(list)


_event_manager = EventManager()


def subscribe(event_type: EventType, listener: Callable):
    _event_manager.subscribe(event_type, listener)


def post_event(event_type: EventType, *args, **kwargs):
    _event_manager.post_event(event_type, *args, **kwargs)


def clear_subscribers():
    _event_manager.clear()
