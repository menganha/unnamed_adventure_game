import pygame
import adventure_game.config as cfg
import json


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface([cfg.TILE_SIZE, cfg.TILE_SIZE])
        self.rect = self.image.get_rect()
        self.image.fill(cfg.RED)
        self.rect.topleft = position


class EnemyGroup(pygame.sprite.Group):
    def __init__(self, map):
        super().__init__()
        self.current_map = map
        self.enemy_positions = []
        self.get_enemy_positions()
        self.create_enemies()

    def get_enemy_positions(self):
        with open(self.current_map) as file:
            self.data = json.load(file)['layers']
        self.enemy_positions = []
        # TODO: Distinguish them from the regular solid objects
        for layer in self.data:
            if layer['type'] == 'objectgroup' and 'enemies' in layer['name']:
                for obj_dict in layer['objects']:
                    self.enemy_positions.append([obj_dict['x'], obj_dict['y']])

    def create_enemies(self):
        for pos in self.enemy_positions:
            self.add(Enemy(pos))

    def update(self, map, in_transition):
        if map != self.current_map:
            self.empty()
            if not in_transition:
                self.current_map = map
                self.get_enemy_positions()
                self.create_enemies()

        # Define how they move
        # Define how they react when player is nearby
        # Check if dead. If so, remove it from the group
