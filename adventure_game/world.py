import pygame
import adventure_game.config as cfg
import json
import re


class Tile(pygame.sprite.Sprite):
    def __init__(self, surface, pos):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self, out_of_bounds):
        self.rect.x -= cfg.SCROLL_VELOCITY * out_of_bounds[0]
        self.rect.y -= cfg.SCROLL_VELOCITY * out_of_bounds[1]
        if (
                self.rect.x <= -cfg.TILE_SIZE and out_of_bounds[0] == 1
                or self.rect.y <= -cfg.TILE_SIZE and out_of_bounds[1] == 1
                or self.rect.x >= cfg.DIS_WIDTH+cfg.TILE_SIZE and out_of_bounds[0] == -1
                or self.rect.y >= cfg.DIS_HEIGHT+cfg.TILE_SIZE and out_of_bounds[1] == -1
                ):
            self.kill()


class World(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.mapLoaded = False
        self.sprite_sheet = pygame.image.load("assets/sprites/RPG Nature Tileset.png")
        self.current_map = r'data/level-x04-y00.json'
        self.map_offset = [0, 0]
        self.in_transition = False
        self.load_map()

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

    def arrange_world(self):
        for layer in self.data:
            if layer['type'] == 'objectgroup':
                continue
            width = layer['width']
            for idx, tile_idx in enumerate(layer['data']):
                if tile_idx == 0:
                    continue
                x = (idx % width)*cfg.TILE_SIZE + self.map_offset[0]
                y = (idx // width)*cfg.TILE_SIZE + self.map_offset[1]
                image = self.tile_dict[tile_idx].convert_alpha()
                Tile(image, (x, y)).add(self)

    def load_map(self):
        self.data = self.load_data()
        self.solid_objects = self.get_solid_objects()
        self.unique_tileset_index = self.get_relevant_tiles()
        self.tile_dict = self.get_tile_dict()
        self.arrange_world()
        if any(offset != 0 for offset in self.map_offset):
            self.in_transition = True
        else:
            self.in_transition = False

    def next_map(self, out_of_bounds):
        match = re.match(r"data/level-x0(\d+)-y0(\d+)\.json", self.current_map)
        x = int(match.group(1)) + int(out_of_bounds[0])
        y = int(match.group(2)) - int(out_of_bounds[1])
        return "data/level-x0{:d}-y0{:d}.json".format(x, y)

    def update(self, out_of_bounds):
        if any(out_of_bounds) and not self.in_transition:
            self.map_offset = [cfg.DIS_WIDTH*out_of_bounds[0], cfg.DIS_HEIGHT*out_of_bounds[1]]
            self.current_map = self.next_map(out_of_bounds)
            self.load_map()

        if any(offset != 0 for offset in self.map_offset):
            super().update(out_of_bounds)
            scroll_vel_vec = [idx*cfg.SCROLL_VELOCITY for idx in out_of_bounds]
            self.map_offset = [offset - vel for offset, vel in zip(self.map_offset, scroll_vel_vec)]
            # TODO: Think of changing all this variables to pygame vectors class
            print(self.map_offset)
        else:
            self.map_offset = [0, 0]
            self.in_transition = False
