import pygame
import config as cfg
import json
import data.maps as maps


class Tile(pygame.sprite.Sprite):
    def __init__(self, surface, pos):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


class World(pygame.sprite.Group):
    def __init__(self, sprite_sheet):
        super().__init__()
        self.data = self.load_data('data/map1.json')
        self.unique_tileset_index = self._get_relevant_tiles()
        self.tile_dict = self._get_tile_dict(sprite_sheet)
        self._arrange_world()

    def _get_relevant_tiles(self):
        unique_tiles = set()
        for layer in self.data:
            unique_tiles = unique_tiles.union(set(layer['data']))
        unique_tiles.remove(0)
        return list(unique_tiles)

    def load_data(self, file):
        with open(file) as f:
            data = json.load(f)['layers']
        return data

    def _get_tile_dict(self, sprite_sheet):
        sheetSize = sprite_sheet.get_size()
        tile_dict = {}
        for iy in range(sheetSize[1]//cfg.TILE_SIZE):
            for ix in range(sheetSize[0]//cfg.TILE_SIZE):
                idx = ix + iy*sheetSize[0]//cfg.TILE_SIZE
                if idx+1 in self.unique_tileset_index:
                    rect = pygame.Rect(ix*cfg.TILE_SIZE, iy*cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                    tile = sprite_sheet.subsurface(rect)
                    tile_dict.update({idx+1: tile})
        return tile_dict

    def _arrange_world(self):
        for layer in self.data:
            width = layer['width']
            for idx, tile_idx in enumerate(layer['data']):
                if tile_idx == 0:
                    continue
                y = (idx // width)*cfg.TILE_SIZE
                x = (idx % width)*cfg.TILE_SIZE
                image = self.tile_dict[tile_idx].convert_alpha()
                Tile(image, (x, y)).add(self)
                #print(x,y, idx, tile_idx)
            print('eureka')
