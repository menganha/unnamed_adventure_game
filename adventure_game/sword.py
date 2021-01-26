# TODO: Make a abstract "Weapon" class from which the Sword and other weapons can be inherited from
import pygame

from adventure_game.action import Action
from adventure_game.direction import Direction
from adventure_game.enemy import Enemy
from adventure_game.enemy_group import EnemyGroup
from adventure_game.config import BLUE


class Sword:
    """
    Main sword weapon.
    """

    def __init__(self, parent_rect: pygame.Rect, depth: int = 20, slash_range: int = 40, extent: int = 10,
                 attack_duration: int = 20):
        # TODO: These Default parameters should be set in the configuration file
        self.parent_rect = parent_rect
        self.depth = depth
        self.slash_range = slash_range
        self.extent = extent
        self.horizontal_rect = pygame.Rect(0, 0, self.slash_range, self.depth)
        self.vertical_rect = pygame.Rect(0, 0, self.depth, self.slash_range)
        self.current_rect = self.horizontal_rect
        self.current_direction = Direction.DOWN
        self.image = None
        self.action = Action(attack_duration)
        self._update_current_rect_and_direction(self.current_direction)

    def attack(self, direction: Direction):
        if self.action.in_progress():
            return
        self._update_current_rect_and_direction(direction)
        self.action.restart()

    def has_hit(self, enemy: Enemy):
        return self.current_rect.colliderect(enemy.hitbox.rect)

    def update(self, enemy_group: EnemyGroup):
        self.action.update()
        if self.action.in_progress():
            for enemy in enemy_group:
                if self.has_hit(enemy): enemy.get_hit(self.current_direction)

    def _update_current_rect_and_direction(self, direction: Direction):
        self.current_direction = direction
        if self.current_direction in (Direction.DOWN, Direction.UP):
            self.current_rect = self.horizontal_rect
        else:
            self.current_rect = self.vertical_rect
        relative_position = self.extent * direction.value
        self.current_rect.center = self.parent_rect.center + relative_position
        self.set_image(BLUE)

    def set_image(self, color):
        self.image = pygame.Surface(self.current_rect.size)
        self.image.fill(color)
        self.image.set_alpha(100)
