import abc
from pathlib import Path
from typing import List, Optional

import esper
import pygame

from yazelc import event_manager


class BaseScene(abc.ABC):
    """ Base implementation for all scenes. This class is abstract and should not be instantiated """

    PLAYER_ENTITY = None

    def __init__(self, window: pygame.Surface, map_name: str, start_tile_x_pos: int, start_tile_y_pos: int,
                 player_components: Optional[List[object]] = None):
        self.window = window
        self.map_data_file = Path('data', f'{map_name}.tmx')
        self.world = esper.World()
        self.start_tile_x_pos = start_tile_x_pos
        self.start_tile_y_pos = start_tile_y_pos

        self.in_scene = True
        self.next_scene = None
        self.last_player_position = None
        if player_components:
            self.PLAYER_ENTITY = self.world.create_entity(*player_components)
        else:
            self.PLAYER_ENTITY = None

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
        self.world.clear_database()  # Is it necessary?
        event_manager.clear_subscribers()

    @abc.abstractmethod
    def on_exit(self):
        pass
