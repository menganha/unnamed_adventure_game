import pygame
import config as cfg
import json


class Tile(pygame.sprite.Sprite):
    def __init__(self, surface, pos):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self, scroll_velocity):
        self.rect.x -= scroll_velocity
        # self.rect.y -= 1
        if self.rect.x <= -cfg.TILE_SIZE or self.rect.y <= -cfg.TILE_SIZE:
            self.kill()


class World(pygame.sprite.Group):
    def __init__(self, sprite_sheet):
        super().__init__()
        self.mapLoaded = False
        self.sprite_sheet = sprite_sheet
        self.load_map('data/map1.json')
        self.map_offset = 0
        self.scroll_velocity = 5
        self.in_transition = False

    def get_relevant_tiles(self):
        unique_tiles = set()
        for layer in self.data:
            if layer['type'] == 'objectgroup':
                continue
            unique_tiles = unique_tiles.union(set(layer['data']))
        unique_tiles.remove(0)
        return list(unique_tiles)

    def load_data(self, file):
        with open(file) as f:
            data = json.load(f)['layers']
        return data

    def get_solid_objects(self):
        solid_objects = []
        for layer in self.data:
            if layer['type'] == 'objectgroup':
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

    def arrange_world(self, offset=0):
        for layer in self.data:
            if layer['type'] == 'objectgroup':
                continue
            width = layer['width']
            for idx, tile_idx in enumerate(layer['data']):
                if tile_idx == 0:
                    continue
                y = (idx // width)*cfg.TILE_SIZE
                x = (idx % width)*cfg.TILE_SIZE + offset
                image = self.tile_dict[tile_idx].convert_alpha()
                Tile(image, (x, y)).add(self)

    def load_map(self, map_name, offset=0):
        self.data = self.load_data(map_name)
        self.solid_objects = self.get_solid_objects()
        self.unique_tileset_index = self.get_relevant_tiles()
        self.tile_dict = self.get_tile_dict()
        self.arrange_world(offset)
        if offset > 0:
            self.in_transition = True
        else:
            self.in_transition = False

    def update(self, out_of_bounds):
        if out_of_bounds and not self.in_transition:
            self.map_offset = cfg.DIS_WIDTH
            self.load_map('data/map2.json', self.map_offset)

        if self.map_offset > 0:
            super().update(self.scroll_velocity)
            self.map_offset -= self.scroll_velocity
        else:
            self.in_transition = False
