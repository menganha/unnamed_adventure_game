import pygame
import json

from adventure_game.enemy import Enemy


class EnemyGroup(pygame.sprite.Group):
    def __init__(self, current_map):
        super().__init__()
        self.current_map = current_map
        self.enemy_list = []
        self.get_enemy_positions()
        self.create_enemies()

    def get_enemy_positions(self):
        with open(self.current_map) as file:
            data = json.load(file)["layers"]
        self.enemy_list = []
        for layer in data:
            if layer["type"] == "objectgroup" and "enemies" in layer["name"]:
                for obj_dict in layer["objects"]:
                    if 'properties' in obj_dict:
                        kind = obj_dict['properties'][0]['value']
                    else:
                        kind = 'jelly'
                    self.enemy_list.append({'pos': (obj_dict["x"], obj_dict["y"]), 'kind': kind})

    def create_enemies(self):
        # TODO: Move this method to a creator/director class
        for enemy in self.enemy_list:
            if enemy['kind'] == 'dragon':
                self.add(Enemy.create_enemy_dragon(enemy['pos']))
            else:
                self.add(Enemy.create_enemy_jelly(enemy['pos']))

    def update(self, delta, new_map, in_transition, physical_objects, player):
        # TODO: This cross-reference is ugly
        if new_map != self.current_map:
            self.empty()
            if not in_transition:
                self.current_map = new_map
                self.get_enemy_positions()
                self.create_enemies()
        else:
            super().update(delta, physical_objects, player)
