import abc

import pygame

import esper


class Scene(abc.ABC):
    """ Base implementation for all scenes"""

    def __init__(self, window: pygame.Surface):
        self.window = window
        self.world = esper.World()
        self.in_scene = True
        self.next_scene = None

    @abc.abstractmethod
    def on_enter(self):
        pass

    def run(self):
        while self.in_scene:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.in_scene = False
            self.world.process()

    @abc.abstractmethod
    def on_exit(self):
        pass


"""
COMMENTS:
    Maps would create a new type of component: doors, to establish enter and exit points
    
    We should make a new system that takes care of transitioning from one scene to the other
    when walking over these enter and exit points
"""
