from collections import defaultdict, deque
from typing import Callable

from yazelc.event_type import EventType


class EventManager:
    """
    Inspired by https://jakubszwajka.github.io/How-to-build-event-system-python/_.

    This event manager is a mix of two main types: events triggering instanstaneously and events accumulating
    and triggered at the end of a frame cycle. These are controlled simply by the variable EVENT_END_OF_FRAME
    """
    EVENT_END_OF_FRAME = [EventType.DEATH, EventType.PAUSE, EventType.RESTART]

    def __init__(self):
        # Uses defaultdict to initialize a list when using a new (missing) key in the dict
        self.subscribers = defaultdict(set)
        self.cached_events = deque()

    def subscribe(self, event_type: EventType, listener: Callable):
        self.subscribers[event_type].add(listener)

    def post_event(self, event_type: EventType, *args, **kwargs):
        if event_type in self.subscribers:
            if (event_type in self.EVENT_END_OF_FRAME) and event_type not in self.cached_events:
                self.cached_events.append((event_type, args, kwargs))
            else:
                for listener in self.subscribers[event_type]:
                    listener(*args, **kwargs)

    def post_cached_events(self):
        while self.cached_events:
            event_type, args, kwargs = self.cached_events.popleft()
            for listener in self.subscribers[event_type]:
                listener(*args, **kwargs)

    def clear(self):
        self.subscribers = defaultdict(set)


_event_manager = EventManager()


def subscribe(event_type: EventType, listener: Callable):
    _event_manager.subscribe(event_type, listener)


def post_event(event_type: EventType, *args, **kwargs):
    _event_manager.post_event(event_type, *args, **kwargs)


def post_cached_events():
    _event_manager.post_cached_events()


def clear_subscribers():
    _event_manager.clear()
