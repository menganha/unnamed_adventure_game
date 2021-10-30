"""
Module to deal with map data
"""
from typing import Iterator, Tuple

import pygame
from pytmx.util_pygame import load_pygame

import components as cmp


class Maps:
    def __init__(self, map_file: str):
        self.tmx_data = load_pygame(map_file)

    def create_map_image(self) -> Iterator[pygame.Surface]:
        for layer_idx in self.tmx_data.visible_tile_layers:
            map_surface = pygame.Surface(
                (self.tmx_data.width * self.tmx_data.tilewidth, self.tmx_data.height * self.tmx_data.tileheight),
                flags=pygame.SRCALPHA)
            for x, y, tile, in self.tmx_data.layers[layer_idx].tiles():
                map_surface.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))
            yield map_surface

    def create_solid_rectangles(self) -> Iterator[Tuple[cmp.Position, cmp.HitBox, cmp.WallTag]]:
        for obj in self.tmx_data.get_layer_by_name('solids'):
            yield cmp.Position(obj.x, obj.y), cmp.HitBox(obj.x, obj.y, obj.width, obj.height), cmp.WallTag()

    def create_doors(self):
        for obj in self.tmx_data.get_layer_by_name('doors'):
            dest_x = obj.properties['dest_x']
            dest_y = obj.properties['dest_y']
            yield cmp.Door(obj.name, dest_x, dest_y), cmp.HitBox(obj.x, obj.y, obj.width, obj.height)

    def get_center_coord_from_tile(self, tile_x_pos: int, tile_y_pos: int) -> (int, int):
        """
        Get tile center absolute coordinates from the position in "tile" coordinates, i.e. the one independent from
        the tile size
        """
        center_x = tile_x_pos * self.tmx_data.tilewidth + int(self.tmx_data.tilewidth / 2)
        center_y = tile_y_pos * self.tmx_data.tilewidth + int(self.tmx_data.tileheight / 2)
        return center_x, center_y
