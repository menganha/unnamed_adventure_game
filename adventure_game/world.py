import pygame
from pygame.math import Vector2
import adventure_game.config as cfg
import json
import re


class World():
    def __init__(self):
        super().__init__()
        self.sprite_sheet = pygame.image.load("assets/sprites/RPG Nature Tileset.png").convert_alpha()
        self.current_map = r'data/level-x04-y00.json'
        self.in_transition = False
        self.map_offset = Vector2((0, 0))
        self.other_offset = Vector2((0, 0))
        self.offset_direction = Vector2((0, 0))
        self.map_image = pygame.Surface((cfg.DIS_WIDTH, cfg.DIS_HEIGHT))
        self.map_image_cache = pygame.Surface((cfg.DIS_WIDTH, cfg.DIS_HEIGHT))
        self.load_map()
        self.arrange_world(self.map_image)

    def load_map(self):
        self.data = self.load_data()
        self.solid_objects = self.get_solid_objects()
        self.unique_tileset_indeces = self.get_relevant_tiles_id()
        self.tile_dict = self.get_tile_surfaces()

    def load_data(self):
        with open(self.current_map) as f:
            data = json.load(f)['layers']
        return data

    def get_solid_objects(self):
        """
        Returns a list of rects representing the solid objects which one can collide
        """
        solid_objects = []
        for layer in self.data:
            if layer['type'] == 'objectgroup' and 'boundaries' in layer['name']:
                layer_objects = [
                    pygame.Rect(obj_dict['x'], obj_dict['y'], obj_dict['width'], obj_dict['height'])
                    for obj_dict in layer['objects']
                    ]
                solid_objects.extend(layer_objects)
        return solid_objects

    def get_relevant_tiles_id(self):
        """
        Get list of unique tiles id's for a map
        """
        unique_tiles = []
        for layer in self.data:
            if layer['type'] == 'objectgroup':
                continue
            unique_tiles.extend(layer['data'])

        unique_tiles = set(unique_tiles)

        if 0 in unique_tiles:  # 0 refers to no tile
            unique_tiles.remove(0)
        return list(unique_tiles)

    def get_tile_surfaces(self):
        """
        Gets the unique tile surfaces
        """
        sheetSize = self.sprite_sheet.get_size()
        tile_dict = {}

        for idx in self.unique_tileset_indeces:
            ix = (idx-1) % (sheetSize[0]//cfg.TILE_SIZE)
            iy = (idx-1) // (sheetSize[0]//cfg.TILE_SIZE)
            rect = pygame.Rect(ix*cfg.TILE_SIZE, iy*cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
            tile = self.sprite_sheet.subsurface(rect)
            tile_dict.update({idx: tile})
        return tile_dict

    def arrange_world(self, destination_surface):
        """
        Blits all tiles into the map image surface
        """
        width = self.sprite_sheet.get_size()[0]//cfg.TILE_SIZE
        for layer in self.data:
            if layer['type'] == 'objectgroup':
                continue
            for idx, tile_idx in enumerate(layer['data']):
                if tile_idx == 0:
                    continue
                x = (idx % width)*cfg.TILE_SIZE
                y = (idx // width)*cfg.TILE_SIZE
                image = self.tile_dict[tile_idx]
                destination_surface.blit(image, (x, y))

    def next_map(self, out_of_bounds: Vector2):
        match = re.match(r"data/level-x0(\d+)-y0(\d+)\.json", self.current_map)
        x = int(match.group(1)) + int(out_of_bounds.x)
        y = int(match.group(2)) - int(out_of_bounds.y)

        return "data/level-x0{:d}-y0{:d}.json".format(x, y)

    def update(self, delta, out_of_bounds: Vector2):

        if any(out_of_bounds) and not self.in_transition:
            self.offset_direction = out_of_bounds
            self.map_offset = self.offset_direction.elementwise()*Vector2((cfg.DIS_WIDTH, cfg.DIS_HEIGHT))
            self.other_offset = Vector2((0, 0))
            self.current_map = self.next_map(out_of_bounds)
            self.load_map()
            self.arrange_world(self.map_image_cache)
            self.in_transition = True

        if self.in_transition:
            if (self.offset_direction.x*self.map_offset.x > 0
                    or self.offset_direction.y*self.map_offset.y > 0):
                shift = int(delta*cfg.SCROLL_VELOCITY)*self.offset_direction
                self.other_offset = self.other_offset - shift
                self.map_offset = self.map_offset - shift
            else:
                self.map_offset = Vector2((0, 0))
                self.other_offset = Vector2((0, 0))
                self.offset_direction = Vector2((0, 0))
                self.in_transition = False
                self.map_image = self.map_image_cache.copy()

    def draw(self, display):
        display.blit(self.map_image, self.other_offset)
        if self.in_transition:
            display.blit(self.map_image_cache, self.map_offset)
