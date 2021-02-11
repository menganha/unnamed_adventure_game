import json
from typing import Dict, List

import pygame
from pygame.math import Vector2

import adventure_game.config as cfg
from adventure_game.direction import Direction


class World:
    """
    Represent the current world map
    """
    UI_OFFSET = Vector2(0, cfg.UI_HEIGHT)

    def __init__(self):
        self.sprite_sheet = pygame.image.load("assets/sprites/RPG Nature Tileset.png").convert_alpha()
        self.map_data_file = r"data/level-x04-y00.json"
        self.offset = Vector2(0, 0)
        self.offset_cache = Vector2(0, cfg.WORLD_HEIGTH)
        self.map_image = pygame.Surface((cfg.WORLD_WIDTH, cfg.WORLD_HEIGTH))
        self.map_image_cache = pygame.Surface((cfg.WORLD_WIDTH, cfg.WORLD_HEIGTH))
        self.map_image_rect = pygame.Rect(0, cfg.UI_HEIGHT, cfg.WORLD_WIDTH, cfg.WORLD_HEIGTH)
        self.data = None
        self.solid_objects = None
        self.unique_tileset_indeces = None
        self.tile_dict = None
        self.load_map()
        self.arrange_world()

    def load_map(self):
        self.data = self.load_data()
        self.solid_objects = self.get_solid_objects()
        self.unique_tileset_indeces = self.get_relevant_tiles_id()
        self.tile_dict = self.get_tile_surfaces()

    def load_data(self):
        with open(self.map_data_file) as file:
            data = json.load(file)["layers"]
        return data

    def get_solid_objects(self) -> List[pygame.Rect]:
        """
        Returns a list of rects representing the solid objects which one can collide
        """
        solid_objects = []
        for layer in self.data:
            if layer["type"] == "objectgroup" and "boundaries" in layer["name"]:
                layer_objects = [
                    pygame.Rect(obj_dict["x"], obj_dict["y"] + cfg.UI_HEIGHT, obj_dict["width"], obj_dict["height"])
                    for obj_dict in layer["objects"]
                ]
                solid_objects.extend(layer_objects)
        return solid_objects

    def get_relevant_tiles_id(self):
        """Get list of unique tiles id's for a map"""
        unique_tiles = set()
        for layer in self.data:
            if layer["type"] == "objectgroup":
                continue
            unique_tiles = unique_tiles.union(set(layer["data"]))

        if 0 in unique_tiles:  # 0 refers to no tile
            unique_tiles.remove(0)
        return list(unique_tiles)

    def get_tile_surfaces(self) -> Dict[str, pygame.Surface]:
        """
        Gets the unique tile surfaces
        """
        # TODO: Think about how to reuse the sprite_sheet class!!!
        sheet_size = self.sprite_sheet.get_size()
        tile_dict = {}

        for idx in self.unique_tileset_indeces:
            ix = (idx - 1) % (sheet_size[0] // cfg.TILE_SIZE)
            iy = (idx - 1) // (sheet_size[0] // cfg.TILE_SIZE)
            rect = pygame.Rect(ix * cfg.TILE_SIZE,
                               iy * cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
            tile = self.sprite_sheet.subsurface(rect)
            tile_dict.update({idx: tile})
        return tile_dict

    def arrange_world(self, in_cache=False):
        """
        Blits all tiles into the map image surface. It can also be chosen to arrange the map on the cache surface
        """
        if not in_cache:
            destination_surface = self.map_image
        else:
            destination_surface = self.map_image_cache

        width = self.sprite_sheet.get_size()[0] // cfg.TILE_SIZE
        for layer in self.data:
            if layer["type"] == "objectgroup":
                continue
            for idx, tile_idx in enumerate(layer["data"]):
                if tile_idx == 0:
                    continue
                x = (idx % width) * cfg.TILE_SIZE
                y = (idx // width) * cfg.TILE_SIZE  # + cfg.UI_HEIGHT
                image = self.tile_dict[tile_idx]
                destination_surface.blit(image, (x, y))

    def move(self, delta: float, velocity: float, direction: Direction):
        self.offset += delta * velocity * direction.value

    def draw(self, display: pygame.Surface) -> pygame.Rect:
        map_coordinates = self.offset + self.UI_OFFSET
        cache_map_coordinates = self.offset_cache + self.offset + self.UI_OFFSET

        display.blit(self.map_image, map_coordinates[:])
        display.blit(self.map_image_cache, cache_map_coordinates[:])

        return self.map_image_rect.copy()  # Best solution one could find to be compatible with the UI
