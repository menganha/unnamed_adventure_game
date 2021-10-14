"""
Module to deal with map data
"""
import pygame
from pytmx.util_pygame import load_pygame

from components import HitBox, Position


class Maps:
    def __init__(self, map_file: str):
        self.tmx_data = load_pygame(map_file)

    def create_map_image(self) -> pygame.Surface:
        map_surface = pygame.Surface(
            (self.tmx_data.width * self.tmx_data.tilewidth, self.tmx_data.height * self.tmx_data.tileheight),
            flags=pygame.SRCALPHA)
        for layer_idx in self.tmx_data.visible_tile_layers:
            for x, y, tile, in self.tmx_data.layers[layer_idx].tiles():
                map_surface.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

        return map_surface

    def create_solid_rectangles(self):
        for obj in self.tmx_data.get_layer_by_name('solids'):
            yield Position(obj.x, obj.y), HitBox(obj.x, obj.y, obj.width, obj.height)
