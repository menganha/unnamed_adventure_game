import abc
from typing import Optional

import pygame

from yazelc import event_manager
from yazelc import zesper


class BaseScene(abc.ABC):
    """
    Base implementation for all scenes. This class is abstract and should not be instantiated.
    """

    def __init__(self, window: pygame.Surface):
        self.window = window
        self.world = zesper.World()
        self.in_scene = True
        self.paused = False
        self.next_scene: Optional['BaseScene'] = None

    @abc.abstractmethod
    def on_enter(self):
        pass

    def run(self):
        while self.in_scene:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.in_scene = False
                    self.next_scene = None
            event_manager.post_cached_events()
            self.world.process()
        event_manager.clear_subscribers()

    @abc.abstractmethod
    def on_exit(self):
        pass
