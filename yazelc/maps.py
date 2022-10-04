"""
Module deals with map data
"""
import logging
from pathlib import Path
from typing import Iterator

import pygame
from pytmx import TiledTileLayer
from pytmx.util_pygame import load_pygame

from yazelc import components as cmp
from yazelc.font import Font
from yazelc.items import CollectableItemType


class Maps:
    DATA_PATH = Path('data')
    DOOR_TARGET_X_STR = 'target_x'
    DOOR_TARGET_Y_STR = 'target_y'
    DOOR_TARGET_STR = 'target_door'
    DOOR_PATH_SEP = ':'
    FOREGROUND_LAYER_NAME = 'foreground'
    OBJECT_LAYER_NAME = 'colliders'
    ENEMY_LAYER_NAME = 'enemy'
    ENEMY_PROP = 'enemy'
    DOOR_LAYER_NAME = 'doors'
    TEXT_PROPERTY = 'text'
    ITEM_PROPERTY = 'item'

    # TODO: Move the "magic" strings below to here

    def __init__(self, map_file_path: Path):
        self.map_file_path = map_file_path
        self.tmx_data = load_pygame(str(map_file_path))
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

    def map_images(self) -> list[pygame.Surface]:
        map_width = self.tmx_data.width * self.tmx_data.tilewidth
        map_height = self.tmx_data.height * self.tmx_data.tileheight
        map_image = pygame.Surface((map_width, map_height), flags=pygame.SRCALPHA)

        foreground_layer_exists = False
        for layer in self.tmx_data.layers:
            if not isinstance(layer, TiledTileLayer):
                continue
            if layer.name == self.FOREGROUND_LAYER_NAME:
                foreground_layer_exists = True
                continue
            for x, y, image, in layer.tiles():
                map_image.blit(image, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

        if foreground_layer_exists:  # Adds an extra image. could be generalized to a group
            map_foreground_image = pygame.Surface((map_width, map_height), flags=pygame.SRCALPHA)
            foreground_layer = self.tmx_data.get_layer_by_name(self.FOREGROUND_LAYER_NAME)
            for x, y, image, in foreground_layer.tiles():
                map_foreground_image.blit(image, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))
            return [map_image, map_foreground_image]
        else:
            logging.info(f'No foreground layer named {self.FOREGROUND_LAYER_NAME} found for the map {self.map_file_path}')
            return [map_image]

    def create_objects(self, font: Font) -> Iterator[tuple]:
        if self.OBJECT_LAYER_NAME not in self.tmx_data.layernames:
            logging.info(f'No {self.OBJECT_LAYER_NAME} layer found for the map {self.map_file_path}')
            return
        for obj in self.tmx_data.get_layer_by_name(self.OBJECT_LAYER_NAME):
            hit_box = cmp.HitBox(obj.x, obj.y, obj.width, obj.height, impenetrable=True)
            position = cmp.Position(obj.x, obj.y)
            if self.TEXT_PROPERTY in obj.properties:
                if obj.properties[self.TEXT_PROPERTY] is None:
                    logging.error('Sign has no dialog')
                dialog = cmp.Dialog(obj.properties[self.TEXT_PROPERTY], font)
                components = (hit_box, dialog)
            elif self.ITEM_PROPERTY in obj.properties:
                # TODO: Default value of all chested items
                collectable = cmp.Collectable(CollectableItemType(obj.properties[self.ITEM_PROPERTY]), 1, in_chest=True)
                components = (hit_box, collectable, position)
            else:
                components = (hit_box,)
            yield components

    def create_doors(self) -> Iterator[tuple]:
        if self.DOOR_LAYER_NAME not in self.tmx_data.layernames:
            logging.info(f'No {self.DOOR_LAYER_NAME} layer found for the map {self.map_file_path}')
            return
        for obj in self.tmx_data.get_layer_by_name(self.DOOR_LAYER_NAME):
            target_x = obj.properties[self.DOOR_TARGET_X_STR]
            target_y = obj.properties[self.DOOR_TARGET_Y_STR]
            map_image_sub_path = obj.properties[self.DOOR_TARGET_STR].split(self.DOOR_PATH_SEP)
            target_door = Path(self.DATA_PATH, *map_image_sub_path)
            hit_box = cmp.HitBox(obj.x, obj.y, obj.width, obj.height, impenetrable=True)
            door = cmp.Door(target_door, target_x, target_y)
            yield door, hit_box

    def create_enemies(self) -> Iterator[tuple]:
        if self.ENEMY_LAYER_NAME not in self.tmx_data.layernames:
            logging.info(f'No {self.ENEMY_LAYER_NAME} layer found for the map {self.map_file_path}')
            return
        for obj in self.tmx_data.get_layer_by_name(self.ENEMY_LAYER_NAME):
            x_pos = obj.x
            y_pos = obj.y
            enemy_type = obj.properties[self.ENEMY_PROP]
            yield x_pos, y_pos, enemy_type

    def get_center_coord_from_tile(self, tile_x_pos: int, tile_y_pos: int) -> (int, int):
        """
        Get tile center absolute coordinates from the position in "tile" coordinates, i.e. the one independent of
        the tile size
        """
        center_x = tile_x_pos * self.tmx_data.tilewidth + int(self.tmx_data.tilewidth / 2)
        center_y = tile_y_pos * self.tmx_data.tilewidth + int(self.tmx_data.tileheight / 2)
        return center_x, center_y
