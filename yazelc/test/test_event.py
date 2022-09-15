import gc
import unittest
from unittest.mock import Mock, call

from yazelc.event import EventManager, EventType, PauseEvent, DeathEvent, CollisionEvent


class PauseClass:
    def on_pause(self, event: PauseEvent):
        pass


class DeathClass:
    def on_death(self, event: DeathEvent):
        pass


class TestEvent(unittest.TestCase):

    def setUp(self) -> None:
        self.event_manager = EventManager()
        instance_with_no_reference = PauseClass()  # It will be garbage collected after we go out of scope of the setup
        self.instance_with_reference = DeathClass()
        self.event_manager.subscribe(EventType.PAUSE, instance_with_no_reference.on_pause)
        self.event_manager.subscribe(EventType.DEATH, self.instance_with_reference.on_death)
        self.event_manager.subscribe(EventType.COLLISION, self.instance_with_reference.on_death)

    def test_clear_all_subscribers(self):
        self.event_manager.clear_subscribers()
        self.assertFalse(self.event_manager.subscribers)

    def test_clear_one_type_of_subscribers(self):
        self.event_manager.clear_subscribers(EventType.COLLISION)
        self.assertFalse(self.event_manager.subscribers[EventType.COLLISION])
        self.assertTrue(self.event_manager.subscribers[EventType.DEATH])

    def test_weak_ref(self):
        gc.collect()
        self.assertFalse(EventType.PAUSE in self.event_manager.subscribers)
        self.assertTrue(EventType.DEATH in self.event_manager.subscribers)

    def test_consume_events(self):
        mock_method = Mock()
        self.event_manager.subscribe(EventType.COLLISION, mock_method)
        event_collision_1 = CollisionEvent(1, 2)
        event_collision_2 = CollisionEvent(4, 2)
        list_event_collision = [event_collision_1, event_collision_2]

        for event in (event_collision_1, list_event_collision):
            with self.subTest(event=event):
                self.event_manager.add_events(event)
                self.event_manager.consume_event_queue()
                calls = [call(evt) for evt in event] if isinstance(event, list) else [call(event)]
                mock_method.assert_has_calls(calls, any_order=False)
                self.assertFalse(self.event_manager.event_queue)


if __name__ == '__main__':
    unittest.main()
