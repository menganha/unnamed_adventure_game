from abc import ABC
import pygame
from pygame.math import Vector2
from typing import Dict

from adventure_game.direction import Direction
from adventure_game.animation import Animation
from adventure_game.state import State


class EnititySprite(pygame.sprite.Sprite):
    """
    Represents the player sprite image
    """

    def __init__(self, initial_position: Vector2, initial_direction: Direction, state: State,
                 group: pygame.sprite.Group, animation_set: Dict[State, Animation]):
        super().__init__(group)
        self.animation_set = animation_set
        self.state = state
        self.current_animation = self._get_animation(state)
        self.image = self.current_animation.next_frame(initial_direction)
        self.rect = self.image.get_rect()
        self.rect.center = initial_position

    def update(self, direction: Direction, position: Vector2, velocity: Vector2, state: State):
        self.rect.center = position
        self.current_animation = self._get_animation(state)
        self.state = state

        if self.state != state:
            self.current_animation.reset()

        self.image = self.current_animation.next_frame(direction)

    def _get_animation(self, state: State):
        try:
            return self.animation_set[state]
        except KeyError:
            return self.animation_set[State.WALK]
