from collections import deque, OrderedDict
from typing import Any


class LastUpdatedOrderedDict(OrderedDict):
    """Store items in the order the keys were last added"""

    def __setitem__(self, key, value):
        if key in self:
            super().__setitem__(key, value)
        else:
            super().__setitem__(key, value)
            self.move_to_end(key)


class EventQueue:

    def __init__(self):
        self._event_queue: deque[Any] = deque()  # collects all events to be fired on the next frame
        self._event_queue_buffer: LastUpdatedOrderedDict[Any] = LastUpdatedOrderedDict()  # collects events with delays

    def enqueue_event(self, event: Any, frames_delay: int = 0):
        if frames_delay:
            self._event_queue_buffer[event] = frames_delay
        else:
            self._event_queue.append(event)

    def popleft(self) -> Any:
        return self._event_queue.popleft()

    def __bool__(self):
        return bool(self._event_queue)

    def process_delayed_events(self):
        """
        Removes one frame of waiting from the delay of the events in the buffer queue.
        If the frame delay reaches zero then it adds the event to the main queue
        """
        events_to_add = deque()
        for event in self._event_queue_buffer:
            self._event_queue_buffer[event] -= 1
            if self._event_queue_buffer[event] == 0:
                events_to_add.append(event)
        self._event_queue.extend(events_to_add)
        for event in events_to_add:
            self._event_queue_buffer.pop(event)

    def clear(self):
        self._event_queue.clear()
        self._event_queue_buffer.clear()
