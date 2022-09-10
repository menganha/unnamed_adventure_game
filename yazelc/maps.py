"""
Module deals with map data
"""
from pathlib import Path
from typing import Iterator, Tuple

import pygame
from pytmx.util_pygame import load_pygame

from yazelc import components as cmp
from yazelc.font import Font


class Maps:
    DOOR_TARGET_X_STR = 'target_x'
    DOOR_TARGET_Y_STR = 'target_y'

    # TODO: Move the "magic" strings below to here

    def __init__(self, map_file: Path):
        self.tmx_data = load_pygame(str(map_file))
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

    def create_map_image(self) -> Iterator[pygame.Surface]:
        for layer_idx in self.tmx_data.visible_tile_layers:
            map_surface = pygame.Surface(
                (self.tmx_data.width * self.tmx_data.tilewidth, self.tmx_data.height * self.tmx_data.tileheight),
                flags=pygame.SRCALPHA)
            for x, y, tile, in self.tmx_data.layers[layer_idx].tiles():
                map_surface.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))
            yield map_surface
            # TODO: Introduce the map depth in the iterator here itself so that the depth specification is encapsulated
            #   in this class

    def create_solid_rectangles(self) -> Iterator[Tuple[cmp.Position, cmp.HitBox, cmp.WallTag]]:
        for obj in self.tmx_data.get_layer_by_name('solids'):
            yield cmp.HitBox(obj.x, obj.y, obj.width, obj.height), cmp.WallTag()

    def create_doors(self):
        for obj in self.tmx_data.get_layer_by_name('doors'):
            target_x = obj.properties[self.DOOR_TARGET_X_STR]
            target_y = obj.properties[self.DOOR_TARGET_Y_STR]
            yield cmp.Door(obj.name, target_x, target_y), cmp.HitBox(obj.x, obj.y, obj.width, obj.height)

    def create_signs(self, font: Font) -> Iterator[Tuple[cmp.InteractorTag, cmp.Dialog, cmp.HitBox]]:
        # TODO: May be generazible to all NPC etc
        # TODO: TEMPORARY FIX!!!!
        try:
            self.tmx_data.get_layer_by_name('interactives')
        except:
            return

        for obj in self.tmx_data.get_layer_by_name('interactives'):
            yield cmp.InteractorTag(), cmp.Dialog(obj.properties['text'], font), cmp.HitBox(obj.x, obj.y, obj.width, obj.height)

    def get_center_coord_from_tile(self, tile_x_pos: int, tile_y_pos: int) -> (int, int):
        """
        Get tile center absolute coordinates from the position in "tile" coordinates, i.e. the one independent of
        the tile size
        """
        center_x = tile_x_pos * self.tmx_data.tilewidth + int(self.tmx_data.tilewidth / 2)
        center_y = tile_y_pos * self.tmx_data.tilewidth + int(self.tmx_data.tileheight / 2)
        return center_x, center_y
