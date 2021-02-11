import json

import pygame
from pygame.math import Vector2

from adventure_game.enemy_creator import EnemyCreator
from adventure_game.enemy_type import EnemyType
from adventure_game.enemy import Enemy


class EnemyGroup:
    """
    Group of enemies
    """

    def __init__(self, map_data_file: str):
        self.sprite_group = pygame.sprite.Group()
        self.enemy_dict = {}
        self.enemy_creator = EnemyCreator()
        self.create_enemies(map_data_file)

    def create_enemies(self, map_data_file: str):
        with open(map_data_file) as file:
            data = json.load(file)["layers"]
        for layer in data:
            if layer["type"] == "objectgroup" and "enemies" in layer["name"]:
                for obj_dict in layer["objects"]:
                    if 'properties' in obj_dict:
                        kind = obj_dict['properties'][0]['value']
                    else:
                        kind = 'jelly'
                    position = Vector2(obj_dict['x'], obj_dict['y'])
                    type_ = EnemyType.get_type_from_value(kind)
                    enemy = self.enemy_creator.create(type_, position, self.sprite_group)
                    enemy.add(self)
                    self.enemy_dict[enemy] = 0

    def remove_enemy(self, enemy: Enemy):
        self.sprite_group.remove(enemy.sprite)
        del self.enemy_dict[enemy]

    def empty(self):
        self.sprite_group.empty()
        for enemy in self.enemies():
            del self.enemy_dict[enemy]

    def update(self, delta: float, physical_objects, player_position: Vector2):
        for enemy in self.enemy_dict:
            enemy.update(delta, physical_objects, player_position)

    def __iter__(self):
        return iter(self.enemies())

    def enemies(self):
        return list(self.enemy_dict)


