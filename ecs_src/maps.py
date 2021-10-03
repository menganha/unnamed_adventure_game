"""
Module to deal with map data
"""
import pygame
import pytmx
from pytmx.util_pygame import load_pygame


def create_map_image(map_file: str) -> pygame.Surface:
    tmx_data = load_pygame(map_file)

    map_surface = pygame.Surface((tmx_data.width * tmx_data.tilewidth, tmx_data.height * tmx_data.tileheight))
    ti = tmx_data.get_tile_image_by_gid
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid, in layer:
                tile = ti(gid)
                if tile:
                    map_surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    return map_surface
