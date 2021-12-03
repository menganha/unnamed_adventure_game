import abc
from pathlib import Path
from typing import List, Optional

import esper
import pygame

from yazelc import event_manager


class BaseScene(abc.ABC):
    """ Base implementation for all scenes. This class is abstract and should not be instantiated """

    PLAYER_ENTITY_ID: Optional[int] = None

    def __init__(self, window: pygame.Surface, map_name: str, start_tile_x_pos: int, start_tile_y_pos: int,
                 player_components: Optional[List[object]] = None):
        self.window = window
        self.map_data_file = Path('data', f'{map_name}.tmx')
        self.world = esper.World()
        self.start_tile_x_pos = start_tile_x_pos
        self.start_tile_y_pos = start_tile_y_pos

        self.in_scene: bool = True
        self.next_scene: Optional['BaseScene'] = None
        if player_components:
            self.PLAYER_ENTITY_ID = self.world.create_entity(*player_components)
        else:
            self.PLAYER_ENTITY_ID = None

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
