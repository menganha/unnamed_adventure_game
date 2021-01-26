from typing import List

import pygame

from adventure_game.action import Action
from adventure_game.direction import Direction
from adventure_game.arrow import Arrow
from adventure_game.enemy_group import EnemyGroup


class Bow:
    """
    Bow weapon and arrows
    """
    SHOOT_COOLDOWN = 10

    def __init__(self, parent_rect: pygame.Rect):
        self.parent_rect = parent_rect
        self.action = Action(self.SHOOT_COOLDOWN)
        self.container = pygame.sprite.Group()
        self.proyectile_image = pygame.image.load('assets/sprites/arrow.png').convert_alpha()

    def attack(self, direction: Direction):
        if self.action.in_progress():
            return
        arrow = Arrow(self.parent_rect.center, direction, self.proyectile_image)
        self.container.add(arrow)
        self.action.restart()

    def update(self, delta: float, physical_obstacles: List[pygame.Rect], enemy_group: EnemyGroup):
        self.action.update()
        self.container.update(delta, physical_obstacles, enemy_group)
