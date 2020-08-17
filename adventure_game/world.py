import pygame
from pygame.math import Vector2
import adventure_game.config as cfg
import json
import re


class Tile(pygame.sprite.Sprite):
    def __init__(self, surface, position):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.position = Vector2(position)

    def update(self, shift, direction: Vector2):
        self.position = self.rect.topleft - shift
        # self.position = self.position - shift
        self.rect.topleft = self.position

        if (
                self.rect.x <= -cfg.TILE_SIZE and direction.x == 1
                or self.rect.y <= -cfg.TILE_SIZE and direction.y == 1
                or self.rect.x >= cfg.DIS_WIDTH+cfg.TILE_SIZE and direction.x == -1
                or self.rect.y >= cfg.DIS_HEIGHT+cfg.TILE_SIZE and direction.y == -1
                ):
            self.kill()

    def update_tile_cache(self, shift, direction: Vector2, group):
        """
        Updates tiles not yet in a group. Adds them once they are within
        the drawing bounds
        """
        if not self.alive():
            self.position = self.rect.topleft - shift
            #self.position = self.position - shift
            self.rect.topleft = self.position

            if (
                    self.rect.x <= cfg.DIS_WIDTH and direction.x == 1
                    or self.rect.y <= cfg.DIS_HEIGHT and direction.y == 1
                    or self.rect.x >= - cfg.TILE_SIZE and direction.x == -1
                    or self.rect.y >= -cfg.TILE_SIZE and direction.y == -1
                    ):
                self.add(group)


class World(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.mapLoaded = False
        self.sprite_sheet = pygame.image.load("assets/sprites/RPG Nature Tileset.png")
        self.current_map = r'data/level-x04-y00.json'
        self.in_transition = False
        self.map_offset = Vector2((0, 0))
        self.direction = Vector2((0, 0))
        self.load_map()
        self.arrange_world()
        self.add_tiles_from_list()

    def get_relevant_tiles(self):
        unique_tiles = set()
        for layer in self.data:
            if layer['type'] == 'objectgroup':
                continue
            unique_tiles = unique_tiles.union(set(layer['data']))
        if 0 in unique_tiles:  # 0 refers to no tile
            unique_tiles.remove(0)
        return list(unique_tiles)

    def load_data(self):
        with open(self.current_map) as f:
            data = json.load(f)['layers']
        return data

    def get_solid_objects(self):
        solid_objects = []
        for layer in self.data:
            if layer['type'] == 'objectgroup' and 'boundaries' in layer['name']:
                for obj_dict in layer['objects']:
                    solid_objects.append(
                        pygame.Rect(obj_dict['x'],
                                    obj_dict['y'],
                                    obj_dict['width'],
                                    obj_dict['height'])
                    )
        return solid_objects

    def get_tile_dict(self):
        sheetSize = self.sprite_sheet.get_size()
        tile_dict = {}
        for iy in range(sheetSize[1]//cfg.TILE_SIZE):
            for ix in range(sheetSize[0]//cfg.TILE_SIZE):
                idx = ix + iy*sheetSize[0]//cfg.TILE_SIZE
                if idx+1 in self.unique_tileset_index:
                    rect = pygame.Rect(ix*cfg.TILE_SIZE, iy*cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                    tile = self.sprite_sheet.subsurface(rect)
                    tile_dict.update({idx+1: tile})
        return tile_dict

    def arrange_world(self):
        self.tile_list = []
        for layer in self.data:
            if layer['type'] == 'objectgroup':
                continue
            width = layer['width']
            for idx, tile_idx in enumerate(layer['data']):
                if tile_idx == 0:
                    continue
                x = (idx % width)*cfg.TILE_SIZE + self.map_offset.x
                y = (idx // width)*cfg.TILE_SIZE + self.map_offset.y
                image = self.tile_dict[tile_idx].convert_alpha()
                self.tile_list.append(Tile(image, (x, y)))

    def add_tiles_from_list(self, shift=None, direction=None):
        if not shift and not direction:
            for tile in self.tile_list:
                tile.add(self)
        else:
            for tile in self.tile_list:
                tile.update_tile_cache(shift, direction, self)

    def load_map(self):
        self.data = self.load_data()
        self.solid_objects = self.get_solid_objects()
        self.unique_tileset_index = self.get_relevant_tiles()
        self.tile_dict = self.get_tile_dict()

    def next_map(self, out_of_bounds: Vector2):
        match = re.match(r"data/level-x0(\d+)-y0(\d+)\.json", self.current_map)
        x = int(match.group(1)) + int(out_of_bounds.x)
        y = int(match.group(2)) - int(out_of_bounds.y)
        return "data/level-x0{:d}-y0{:d}.json".format(x, y)

    def update(self, delta, out_of_bounds: Vector2):
        if any(out_of_bounds) and not self.in_transition:
            self.direction = out_of_bounds
            self.map_offset = self.direction.elementwise()*Vector2((cfg.DIS_WIDTH, cfg.DIS_HEIGHT))
            self.current_map = self.next_map(out_of_bounds)
            self.load_map()
            self.arrange_world()
            self.in_transition = True

        # if all(floor(offset) == 0 for offset in self.map_offset):
        if (self.direction.x*self.map_offset.x <= 0
                and self.direction.y*self.map_offset.y <= 0):
            self.map_offset = Vector2((0, 0))
            self.in_transition = False
        else:
            shift = int(delta*cfg.SCROLL_VELOCITY)*self.direction
            self.map_offset = self.map_offset - shift
            super().update(shift, self.direction)
            self.add_tiles_from_list(shift, self.direction)
