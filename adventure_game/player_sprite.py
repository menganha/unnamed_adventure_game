from pathlib import Path

import pygame
from pygame.math import Vector2

from adventure_game.animation import Animation
from adventure_game.animation_data import AnimationData
from adventure_game.direction import Direction
from adventure_game.entity_sprite import EnititySprite
from adventure_game.sprite_sheet import SpriteSheet
from adventure_game.state import State


class PlayerSprite(EnititySprite):
    """
    Represents the player sprite image
    """
    FRAME_NUMBER = 6
    ATTACK_FRAME_NUMBER = 5
    SPRITE_SIZE = (32, 32)
    IDLE_FRAME_DURATION = 15
    WALK_FRAME_DURATION = 10
    ATTACK_FRAME_DURATION = 3

    def __init__(self, initial_position: Vector2, initial_direction: Direction, state: State,
                 group: pygame.sprite.Group):
        idle_sprite_sheet = SpriteSheet(Path('./assets/sprites/player/idle.png'), self.SPRITE_SIZE)
        walk_sprite_sheet = SpriteSheet(Path('./assets/sprites/player/walk.png'), self.SPRITE_SIZE)
        attack_sprite_sheet = SpriteSheet(Path('./assets/sprites/player/attack.png'), self.SPRITE_SIZE)

        idle_animation_data = AnimationData(self.FRAME_NUMBER, self.IDLE_FRAME_DURATION)
        walk_animation_data = AnimationData(self.FRAME_NUMBER, self.WALK_FRAME_DURATION)
        attack_animation_data = AnimationData(self.ATTACK_FRAME_NUMBER, self.ATTACK_FRAME_DURATION)

        animation_set = {
            State.IDLE: Animation(idle_sprite_sheet, idle_animation_data),
            State.WALK: Animation(walk_sprite_sheet, walk_animation_data),
            State.ATTACK: Animation(attack_sprite_sheet, attack_animation_data)
        }

        super().__init__(initial_position, initial_direction, state, group, animation_set)
