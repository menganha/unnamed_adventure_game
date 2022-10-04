from __future__ import annotations

from abc import ABC
from collections import defaultdict, deque
from collections.abc import Callable
from enum import Enum, auto
from types import MethodType
from typing import TYPE_CHECKING, Union, TypeVar
from weakref import ref, WeakMethod

if TYPE_CHECKING:
    from yazelc.items import CollectableItemType


class EventType(Enum):
    DEATH = auto()
    PAUSE = auto()
    COLLISION = auto()
    HUD_UPDATE = auto()
    RESTART = auto()
    CLOCK = auto()


class Event(ABC):
    EVENT_TYPE = None


class DeathEvent(Event):
    EVENT_TYPE = EventType.DEATH


class PauseEvent(Event):
    EVENT_TYPE = EventType.PAUSE


class RestartEvent(Event):
    EVENT_TYPE = EventType.RESTART


class CollisionEvent(Event):
    EVENT_TYPE = EventType.COLLISION

    def __init__(self, ent_1: int, ent_2: int):
        self.ent_1 = ent_1
        self.ent_2 = ent_2


class HudUpdateEvent(Event):
    EVENT_TYPE = EventType.HUD_UPDATE

    def __init__(self, collectable_item_type: CollectableItemType, value: int):
        self.pickable_item_type = collectable_item_type
        self.value = value


class ClockEvent(Event):
    EVENT_TYPE = EventType.CLOCK

    def __init__(self, entity_id: int, **kwargs):
        self.entity_id = entity_id
        self.kwargs = kwargs


_EVENT = TypeVar('_EVENT', bound=Event)  # used for the static type checker


class EventManager:
    """
    Event manager that consumes (publish or broadcast) all collected events in one go
    Uses a defaultdict for subscriber storage to initialize a set when using a new (missing) key in the dict
    """

    def __init__(self):
        self.subscribers = defaultdict(set)
        self.event_queue = deque()

    def subscribe(self, event_type: EventType, listener: Callable[[_EVENT], None]):

        if isinstance(listener, MethodType):
            self.subscribers[event_type].add(WeakMethod(listener, self._make_callback(event_type)))
        else:
            self.subscribers[event_type].add(ref(listener, self._make_callback(event_type)))

    def add_events(self, events: Union[Event, list[type(Event)]]):
        if isinstance(events, deque):
            self.event_queue.extend(events)
        else:
            self.event_queue.append(events)

    def consume_event_queue(self):
        while self.event_queue:
            event = self.event_queue.popleft()
            for listener in self.subscribers[event.EVENT_TYPE]:
                listener()(event)

    def clear_subscribers(self, event_type: EventType = None):
        if event_type:
            self.subscribers[event_type] = set()
        else:
            self.subscribers = defaultdict(set)

    def clear(self):
        self.subscribers = defaultdict(set)
        self.event_queue = deque()

    def _make_callback(self, event_type: EventType):
        """Create a callback to remove dead handlers."""

        def callback(weak_method):
            self.subscribers[event_type].remove(weak_method)
            if not self.subscribers[event_type]:
                del self.subscribers[event_type]

        return callback
