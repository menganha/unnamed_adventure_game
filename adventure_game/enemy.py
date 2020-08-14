import pygame
import adventure_game.config as cfg
import json


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface([16, 16])
        self.rect = self.image.get_rect()
        self.image.fill(cfg.GREEN)
        self.rect.topleft = position
        self.blink_time = 0

    def get_hit(self):
        self.blink_time = 10

    def update(self):
        if self.blink_time >= 0:
            if self.blink_time % 4 < 2:
                color = cfg.GREEN
            else:
                color = cfg.WHITE
            self.image.fill(color)
            self.blink_time -= 1


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
        else:
            super().update()

        # Define how they move
        # Define how they react when player is nearby
        # Check if dead. If so, remove it from the group
