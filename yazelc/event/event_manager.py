from collections import defaultdict
from collections.abc import Callable
from types import MethodType
from typing import TypeVar, Any
from weakref import ref, WeakMethod

_EVENT = TypeVar('_EVENT')  # used for the static type checker for admitting any subclass
_EVENT_TYPE = type[_EVENT]


class EventManager:
    """
    Event manager that consumes (publish or broadcast) all collected events in one go
    Uses a defaultdict for subscriber storage to initialize a set when using a new (missing) key in the dict
    """

    def __init__(self):
        self.subscribers = defaultdict(set)
        from yazelc.event import events  # TODO: think of putting this on the top without causing circular imports
        self._event_types = [getattr(events, attr) for attr in vars(events)
                             if isinstance(getattr(events, attr), type) and attr.lower().endswith('event')]

    def subscribe(self, event_type: _EVENT_TYPE, handler: Callable[[_EVENT], None]):
        """ Subscribe handler method to event type """
        reference_type = self._reference_type(handler)
        callback_on_garbage_collection = self._make_callback(event_type)
        self.subscribers[event_type].add(reference_type(handler, callback_on_garbage_collection))

    def subscribe_class(self, instance: Any):
        """ Subscribe all bound methods of type if they have the right name format: on_{event_type} """
        for type_ in self._event_types:
            method_name = f'on_{type_.__name__.lower().replace("event", "")}'
            if hasattr(instance, method_name):
                self.subscribe(type_, getattr(instance, method_name))

    def unsubscribe_class(self, instance: Any):
        for type_ in self._event_types:
            method_name = f'on_{type_.__name__.lower().replace("event", "")}'
            if hasattr(instance, method_name):
                self.remove_handler(type_, getattr(instance, method_name))

    def dispatch_event(self, event: _EVENT):
        for listener in self.subscribers[type(event)]:
            listener()(event)

    def remove_handler(self, event_type: _EVENT_TYPE, handler: Callable[[_EVENT], None]):
        reference_type = self._reference_type(handler)
        handler_reference = reference_type(handler)

        if handler_reference not in self.subscribers.get(event_type, []):
            return

        self.subscribers[event_type].remove(handler_reference)

        if not self.subscribers[event_type]:
            self.subscribers.pop(event_type)

    def remove_all_handlers(self, event_type: _EVENT_TYPE = None):
        if event_type:
            self.subscribers.pop(event_type, None)
        else:
            self.subscribers = defaultdict(set)

    def _make_callback(self, event_type: _EVENT_TYPE):
        """ Creates a callback to remove dead handlers """

        def callback(weak_method):
            self.subscribers[event_type].remove(weak_method)
            if not self.subscribers[event_type]:
                self.subscribers.pop(event_type)

        return callback

    @staticmethod
    def _reference_type(handler: Callable) -> Callable:
        if isinstance(handler, MethodType):
            reference_type = WeakMethod
        else:
            reference_type = ref
        return reference_type
