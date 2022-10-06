"""
Module deals with map data
"""
import json
import logging
import os.path
from pathlib import Path
from typing import Iterator, Optional
from xml.etree import ElementTree

import pygame
from pytmx import TiledTileLayer, TiledMap, util_pygame

import zesper
from yazelc import components as cmp
from yazelc.font import Font
from yazelc.items import CollectableItemType
from yazelc.resource_manager import ResourceManager


class WorldMap:
    WORLD_MAP_SUFFIX = '.world'

    def __init__(self, world_map_file_path: Path):
        self.file_path = world_map_file_path
        with open(self.file_path) as file:
            self._data = json.load(file)

    def get_needed_images_path(self) -> list[Path]:
        """ Gets the file paths of minimal subset of images to load all the maps of this world """
        image_paths = []
        for single_map in self._data['maps']:
            file_name = single_map['fileName']
            file_path = Path(self.file_path.parent, file_name)
            tree = ElementTree.parse(file_path)
            for node in tree.findall('.//tileset'):
                relative_path = node.get('source')
                tileset_path = Path(self.file_path.parent, relative_path)
                tileset_tree = ElementTree.parse(tileset_path)
                for tileset_node in tileset_tree.findall('.//image'):
                    image_relative_path = tileset_node.get('source')
                    image_path = Path(tileset_path.parent, image_relative_path)
                    image_paths.append(image_path)
        return image_paths

    @staticmethod
    def get_world_map_file_path(map_file_path: Path) -> Path:
        list_world_map_files = list(map_file_path.parent.glob(f'*{WorldMap.WORLD_MAP_SUFFIX}'))
        if len(list_world_map_files) != 1:
            raise RuntimeError(f'None or more than one world file on the folder f{map_file_path.parent}')
        return list_world_map_files[0]

    @classmethod
    def from_map_file_path(cls, map_file_path: Path) -> 'WorldMap':
        world_map_file_path = cls.get_world_map_file_path(map_file_path)
        return cls(world_map_file_path)


class Map:
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

    def __init__(self, map_file_path: Path, resource_manager: ResourceManager):
        self.map_file_path = map_file_path
        self.resource_manager = resource_manager
        self.tmx_data = TiledMap(str(map_file_path), image_loader=self.yazelc_tiled_image_loader)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.map_layer_entities = []

    def get_map_images(self) -> list[pygame.Surface]:
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

    def add_map_to_the_world(self, world: zesper.World):
        for idx, map_layer in enumerate(self.get_map_images()):
            layer_entity_id = world.create_entity()
            world.add_component(layer_entity_id, cmp.Position(x=0, y=0))
            depth = 1000 * idx
            world.add_component(layer_entity_id, cmp.Renderable(image=map_layer, depth=depth))
            self.map_layer_entities.append(layer_entity_id)

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

    def yazelc_tiled_image_loader(self, filename: str, color_key: Optional[util_pygame.ColorLike], **kwargs):
        """
        pytmx image loader for pygame

        Parameters:
            filename: filename, including path, to load
            color_key: color_key for the image

        Returns:
            function to load tile images

        """
        if color_key:
            color_key = pygame.Color("#{0}".format(color_key))

        pixelalpha = kwargs.get("pixelalpha", True)
        basename_no_ext = os.path.splitext(os.path.basename(filename))[0]
        image = self.resource_manager.get_texture(basename_no_ext)

        def load_image(rect=None, flags=None):
            if rect:
                try:
                    tile = image.subsurface(rect)
                except ValueError:
                    util_pygame.logger.error("Tile bounds outside bounds of tileset image")
                    raise
            else:
                tile = image.copy()

            if flags:
                tile = util_pygame.handle_transformation(tile, flags)

            tile = util_pygame.smart_convert(tile, color_key, pixelalpha)
            return tile

        return load_image
