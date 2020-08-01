import pygame
import config as cfg
import data.maps as maps


class Tile(pygame.sprite.Sprite):
    def __init__(self, surface, rect):
        super().__init__()
        self.image = surface
        self.rect = rect


class World(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.unique_tileset_index = self._get_relevant_tiles()
        self.tile_dict = self._get_tile_dict()
        self._arrange_world()

    def _get_relevant_tiles(self):
        flat_list = [item for sublist in maps.world_1 for item in sublist]
        return list(set(flat_list))

    def _get_tile_dict(self):
        spriteSheet = pygame.image.load("./assets/sprites/overworld.png").convert_alpha()
        sheetSize = spriteSheet.get_size()
        tile_list = {}
        for iy in range(sheetSize[1]//cfg.TILE_SIZE):
            for ix in range(sheetSize[0]//cfg.TILE_SIZE):
                idx = ix + iy*sheetSize[0]//cfg.TILE_SIZE
                if idx in self.unique_tileset_index:
                    rect = pygame.Rect(ix*cfg.TILE_SIZE, iy*cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                    tile = spriteSheet.subsurface(rect)
                    tile_list.update({idx: tile})
        return tile_list

    def _arrange_world(self):
        for iy, horiz_slice in enumerate(maps.world_1):
            for ix, tile_index in enumerate(horiz_slice):
                x = ix*cfg.TILE_SIZE
                y = iy*cfg.TILE_SIZE
                image = self.tile_dict[tile_index].convert_alpha()
                rect = image.get_rect()
                rect.topleft = (x, y)
                Tile(image, rect).add(self)
