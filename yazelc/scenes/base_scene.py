import abc
from typing import Optional

import pygame

from yazelc import zesper
from yazelc.clock import Clock
from yazelc.event import EventManager


class BaseScene(abc.ABC):
    """
    Base implementation for all scenes. This class is abstract and should not be instantiated.
    """

    def __init__(self, window: pygame.Surface):
        self.window: pygame.Surface = window
        self.world: zesper.World = zesper.World()
        self.event_manager: EventManager = EventManager()
        self.clock: Clock = Clock()
        self.in_scene: bool = True
        self.paused: bool = False
        self.next_scene: Optional['BaseScene'] = None

    @abc.abstractmethod
    def on_enter(self):
        pass

    def run(self):
        self.in_scene = True
        while self.in_scene:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.in_scene = False
                    self.next_scene = None
            self._process_clock_events()
            self._process_event_queue()
            self.world.process()
        self.event_manager.remove_all_handlers()

    @abc.abstractmethod
    def on_exit(self):
        pass

    def empty_queues(self):
        for proc in self.world._processors:
            proc.events.clear()
        self.event_manager.event_queue.clear()

    def _process_event_queue(self):
        """
        1. Recollect all events from the active system
        2. Process them
        3. If some events produced within other events, start again from 1
        """
        for proc in self.world._processors:
            self.event_manager.add_events(proc.events)
            proc.events.clear()

        while self.event_manager.event_queue:
            self.event_manager.consume_event_queue()

            for proc in self.world._processors:
                self.event_manager.add_events(proc.events)
                proc.events.clear()

    def _process_clock_events(self):
        for proc in self.world._processors:
            self.clock.timer_events.extend(proc.timers)
            proc.timers.clear()
        self.clock.tick()
