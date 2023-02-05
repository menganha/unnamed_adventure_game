from abc import ABC
from collections import defaultdict
from collections.abc import Callable
from types import MethodType
from typing import TypeVar
from weakref import ref, WeakMethod


class Event(ABC):
    pass


_EVENT = TypeVar('_EVENT', bound=Event)  # used for the static type checker for admitting any subclass


class EventManager:
    """
    Event manager that consumes (publish or broadcast) all collected events in one go
    Uses a defaultdict for subscriber storage to initialize a set when using a new (missing) key in the dict
    """

    def __init__(self):
        self.subscribers = defaultdict(set)

    def subscribe(self, event_type: type[Event], handler: Callable[[_EVENT], None]):
        """ Subscribe handler method to event type """
        if isinstance(handler, MethodType):
            self.subscribers[event_type].add(WeakMethod(handler, self._make_callback(event_type)))
        else:
            self.subscribers[event_type].add(ref(handler, self._make_callback(event_type)))

    def dispatch_event(self, event: Event):
        for listener in self.subscribers[type(event)]:
            listener()(event)

    def remove_all_handlers(self, event_type: type[Event] = None):
        if event_type:
            self.subscribers[event_type] = set()
        else:
            self.subscribers = defaultdict(set)

    def _make_callback(self, event_type: type[Event]):
        """ Creates a callback to remove dead handlers """

        def callback(weak_method):
            self.subscribers[event_type].remove(weak_method)
            if not self.subscribers[event_type]:
                del self.subscribers[event_type]

        return callback
