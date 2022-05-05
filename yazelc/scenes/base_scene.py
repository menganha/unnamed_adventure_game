import abc
from pathlib import Path
from typing import List, Optional

import pygame

from yazelc import event_manager
from yazelc import zesper


class BaseScene(abc.ABC):
    """ Base implementation for all scenes. This class is abstract and should not be instantiated """

    def __init__(self, window: pygame.Surface, map_name: str, start_tile_x_pos: int, start_tile_y_pos: int,
                 player_components: Optional[List[object]] = None):
        self.window = window
        self.map_data_file = Path('data', f'{map_name}.tmx')
        self.world = zesper.World()
        self.start_tile_x_pos = start_tile_x_pos
        self.start_tile_y_pos = start_tile_y_pos

        self.in_scene = True
        self.paused = False
        self.next_scene: Optional['BaseScene'] = None
        self.scene_processors: List[zesper.Processor] = []

        if player_components:
            self.world.player_entity_id = self.world.create_entity(*player_components)

    @abc.abstractmethod
    def on_enter(self):
        pass

    def run(self):
        while self.in_scene:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.in_scene = False
                    self.next_scene = None
            self.world.process()
        event_manager.clear_subscribers()

    @abc.abstractmethod
    def on_exit(self):
        pass
