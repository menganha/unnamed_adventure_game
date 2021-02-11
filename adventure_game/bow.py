from typing import List

import pygame

from adventure_game.action import Action
from adventure_game.arrow import Arrow
from adventure_game.direction import Direction


class Bow:
    """
    Bow weapon and arrows
    """
    SHOOT_COOLDOWN = 20

    def __init__(self, parent_rect: pygame.Rect, parent_group: pygame.sprite.Group):
        self.parent_rect = parent_rect
        self.action = Action(self.SHOOT_COOLDOWN)
        self.quiver = pygame.sprite.Group()
        self.parent_group = parent_group
        self.proyectile_image = pygame.image.load('assets/sprites/arrow.png').convert_alpha()

    def attack(self, direction: Direction):
        if self.action.in_progress():
            return
        arrow = Arrow(self.parent_rect.center, direction, self.proyectile_image)
        arrow.add(self.parent_group, self.quiver)
        self.action.restart()

    def update(self, delta: float, physical_obstacles: List[pygame.Rect]):
        self.action.update()
        self.quiver.update(delta, physical_obstacles)
