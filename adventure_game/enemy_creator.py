from pathlib import Path

import pygame
from pygame.math import Vector2

from adventure_game.animation import Animation
from adventure_game.animation_data import AnimationData
from adventure_game.direction import Direction
from adventure_game.enemy import Enemy
from adventure_game.entity_sprite import EnititySprite
from adventure_game.sprite_sheet import SpriteSheet
from adventure_game.state import State
from adventure_game.enemy_type import EnemyType


class EnemyCreator:
    """
    Responsible to instantiate enemies
    """
    # TODO: LOAD ALL SPRITES IN CONSTRUCTOR!!
    def __init__(self):
        self.create_methods = {
            EnemyType.DRAGON: self._create_dragon,
            EnemyType.JELLY: self._create_jelly
        }

    def create(self, enemy_type: EnemyType, position: Vector2, group: pygame.sprite.Group) -> Enemy:
        return self.create_methods[enemy_type](position, group)

    @staticmethod
    def _create_jelly(position: Vector2, group: pygame.sprite.Group) -> Enemy:
        sprite_size = (16, 16)
        frame_number = 3
        frame_duration = 10
        sprite_sheet_path = Path('./assets/sprites/enemy/jelly.png')
        walk_sprite_sheet = SpriteSheet(sprite_sheet_path, sprite_size)
        walk_animation_data = AnimationData(frame_number, frame_duration)
        animation_set = {State.WALK: Animation(walk_sprite_sheet, walk_animation_data)}
        direction = Direction.random_direction()
        sprite = EnititySprite(position, direction, State.IDLE, group, animation_set)
        return Enemy(position, direction, 2, sprite)

    @staticmethod
    def _create_dragon(position: Vector2, group: pygame.sprite.Group) -> Enemy:
        sprite_size = (64, 64)
        frame_number = 2
        frame_duration = 15
        sprite_sheet_path = Path('./assets/sprites/enemy/dragon.png')
        walk_sprite_sheet = SpriteSheet(sprite_sheet_path, sprite_size)
        walk_animation_data = AnimationData(frame_number, frame_duration)
        animation_set = {State.WALK: Animation(walk_sprite_sheet, walk_animation_data)}
        direction = Direction.LEFT
        sprite = EnititySprite(position, direction, State.IDLE, group, animation_set)
        return Enemy(position, direction, 2, sprite)
