import pygame
import json

from adventure_game.enemy import Enemy


class EnemyGroup(pygame.sprite.Group):
    def __init__(self, map_data_file: str):
        super().__init__()
        self.map_data_file = map_data_file
        self.enemy_list = []
        self.get_enemy_positions(map_data_file)
        self.create_enemies()

    def get_enemy_positions(self, map_data_file: str):
        with open(map_data_file) as file:
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
        for enemy in self.enemy_list:
            if enemy['kind'] == 'dragon':
                self.add(Enemy.create_enemy_dragon(enemy['pos']))
            else:
                self.add(Enemy.create_enemy_jelly(enemy['pos']))
